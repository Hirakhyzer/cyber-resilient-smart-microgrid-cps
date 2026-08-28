# Threat Model

## In scope
Synthetic, in-memory manipulations of microgrid telemetry and communication: sensor bias/FDI, SOC spoofing, PV/load measurement manipulation, voltage/frequency bias, replay, metadata-rewritten replay, sensor freeze, packet loss, latency, jitter, and combined cyber/physical scenarios such as attacks during islanding.

## Out of scope
Real utility/DER credentials, operational IP addresses, vendor-specific exploit chains, malware, destructive commands, bypass procedures, protection settings, or protocol-specific payloads intended for live infrastructure.

The purpose is defensive detection, resilience measurement, and control research in an isolated simulator.
