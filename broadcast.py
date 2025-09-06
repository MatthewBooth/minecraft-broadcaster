#!/usr/bin/env python3
import argparse
import math
import os
import signal
import socket
import time

MC_ADDR = ("224.0.2.60", 4445)  # Minecraft LAN multicast (IPv4)


def build_entries(raw: str) -> list[tuple[str, int]]:
    out = []
    for chunk in (raw or "").split(","):
        line = chunk.strip()
        if not line:
            continue
        try:
            motd, port = line.split("|", 1)
            motd = motd.strip()
            port = int(port.strip())
            if not motd or not 1 <= port <= 65535:
                raise ValueError
            out.append((motd, port))
        except ValueError:
            print(f"[WARN] Skipping invalid broadcast entry: {line}", flush=True)
    return out


def parse_interval(raw: str) -> float:
    try:
        interval = float(raw)
    except ValueError as exc:
        raise ValueError("BROADCAST_INTERVAL_SECONDS must be a positive number") from exc
    if not math.isfinite(interval) or interval <= 0:
        raise ValueError("BROADCAST_INTERVAL_SECONDS must be a positive number")
    return interval


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send Minecraft LAN server announcements over IPv4 multicast."
    )
    parser.add_argument(
        "--broadcast",
        action="append",
        metavar="MOTD|PORT",
        help="server announcement to send; may be repeated (defaults to BROADCASTS)",
    )
    parser.add_argument(
        "--interval",
        metavar="SECONDS",
        help="seconds between announcement rounds (defaults to BROADCAST_INTERVAL_SECONDS or 1)",
    )
    args = parser.parse_args(argv)

    raw_broadcasts = args.broadcast if args.broadcast is not None else [os.getenv("BROADCASTS", "")]
    entries: list[tuple[str, int]] = []
    for raw in raw_broadcasts:
        entries.extend(build_entries(raw))
    if not entries:
        parser.error("provide at least one valid --broadcast or BROADCASTS entry")

    try:
        interval = parse_interval(
            args.interval
            if args.interval is not None
            else os.getenv("BROADCAST_INTERVAL_SECONDS", "1")
        )
    except ValueError as exc:
        parser.error(str(exc))
    args.entries = entries
    args.interval_seconds = interval
    return args


def run(entries: list[tuple[str, int]], interval: float) -> None:
    # UDP socket for IPv4 multicast
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # TTL 1 keeps it on the LAN
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    # (Optional) pick interface via IP_MULTICAST_IF if you need; default route usually fine

    payloads = [f"[MOTD]{motd}[/MOTD][AD]{port}[/AD]".encode() for motd, port in entries]

    print(f"[INFO] Announcing every {interval}s to {MC_ADDR[0]}:{MC_ADDR[1]}", flush=True)
    for motd, port in entries:
        print(f"[INFO]  - {motd} -> {port}", flush=True)

    stop = False

    def handle(*_: object) -> None:
        nonlocal stop
        stop = True

    signal.signal(signal.SIGTERM, handle)
    signal.signal(signal.SIGINT, handle)

    while not stop:
        for p in payloads:
            try:
                sock.sendto(p, MC_ADDR)
            except OSError as exc:
                print(f"[WARN] sendto failed: {exc}", flush=True)
        time.sleep(interval)

    print("[INFO] Exiting cleanly.", flush=True)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    run(args.entries, args.interval_seconds)


if __name__ == "__main__":
    main()
