/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<8>  UDP_PROTOCOL = 0x11;
const bit<16> TYPE_IPV4 = 0x800;
const bit<16> TYPE_RTP = 0x88ff;

#define MAX_HOPS 9

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<32> switchID_t;
typedef bit<32> qdepth_t;
typedef bit<32> rtpAddr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header rtp_t {
    bit<2>      version;
    bit<1>      P;
    bit<1>      X;
    bit<4>      CC;
    bit<1>      M;
    bit<7>      PT;
    bit<16>     SequenceNumber;
    bit<32>     timestamp;
    bit<32>     SSRC;
    bit<32>     CSRC;
    rtpAddr_t   srcAddr;
    rtpAddr_t   dstAddr;
}

struct metadata {
    bit<14>                 ecmp_select;
}

struct headers {
    ethernet_t         ethernet;
    ipv4_t             ipv4;
    rtp_t              rtp;
}

error { IPHeaderTooShort }

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_RTP: parse_rtp;
            default: accept;
        }
    }
    
    state parse_rtp {
        packet.extract(hdr.rtp);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
    }
}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop(standard_metadata);
    }
    
    action set_ecmp_select(bit<16> ecmp_base, bit<32> ecmp_count) {
        hash(meta.ecmp_select,
            HashAlgorithm.crc16,
            ecmp_base,
            { hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr,
              hdr.ipv4.protocol,
              hdr.rtp.srcAddr,
              hdr.rtp.dstAddr },
            ecmp_count);
    }
    action set_nhop(bit<48> nhop_dmac, bit<32> nhop_ipv4, bit<32> nhop_rtp, bit<9> port) {
        hdr.ethernet.dstAddr = nhop_dmac;
        hdr.ipv4.dstAddr = nhop_ipv4;
        hdr.rtp.dstAddr = nhop_rtp;
        standard_metadata.egress_spec = port;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }
    table ecmp_group_1 {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            drop;
            set_ecmp_select;
        }
        size = 1024;
    }
    table ecmp_group_2 {
        key = {
            hdr.rtp.dstAddr: lpm;
        }
        actions = {
            drop;
            set_ecmp_select;
        }
        size = 1024;
    }
    table ecmp_nhop_1 {
        key = {
            meta.ecmp_select: exact;
        }
        actions = {
            drop;
            set_nhop;
        }
        size = 2;
    }
     table ecmp_nhop_2 {
        key = {
            meta.ecmp_select: exact;
        }
        actions = {
            drop;
            set_nhop;
        }
        size = 2;
    }

    apply {
        if (hdr.ipv4.isValid() && hdr.ipv4.ttl > 0) {
            ecmp_group_1.apply();
            ecmp_nhop_1.apply();
        }
        if (hdr.rtp.isValid()) {
            ecmp_group_2.apply();
            ecmp_nhop_2.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

    action rewrite_mac(bit<48> smac) {
        hdr.ethernet.srcAddr = smac;
    }
    action drop() {
        mark_to_drop(standard_metadata);
    }
    table send_frame {
        key = {
            standard_metadata.egress_port: exact;
        }
        actions = {
            rewrite_mac;
            drop;
        }
        size = 256;
    }
    apply {
        send_frame.apply();
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {
        update_checksum(
            hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.rtp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
