module:

import fmt
import os

global gPort = 8181_u16

global gReply = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 12\r\n\r\nHello World!";

pub fun htons(x u16) u16:
    return x << 8 | x >> 8


macro make_blob# EXPR ($e EXPR) []:
    make_span(bitwise_as(@$e, ^u8), size_of(type_of($e)))

macro make_mut_blob# EXPR ($e EXPR) []:
    make_span(bitwise_as(@$e, ^!u8), size_of(type_of($e)))

fun main(argc s32, argv ^^u8) s32:
    trylet server_fd os\FD = os\Socket(os\AddressFamily.INET, os\SocketType.STREAM, 0), err:
        return 1

    fmt\print#("Server fd: ",  unwrap(server_fd), "\n")
    let! res void

    ref let val = 1_u32
    tryset res = os\SetSocketOptions(server_fd, os\SocketLevel.SOCKET, os\SocketOption.SO_REUSEADDR,
                                  make_blob#(val)), err:
        return 1

    ref let addr = {os\SockAddrIn: os\AddressFamily.INET, htons(gPort), {[4]u8: 0, 0, 0, 0}}

    tryset res = os\Bind(server_fd, make_blob#(addr)), err:
        return 1

    tryset res = os\Listen(server_fd, 3), err:
        return 1

    fmt\print#("Listening on port: ", gPort, "\n")

    while true:
        fmt\print#("Waiting for connection\n")
        ref let addr os\SockAddrIn = undef
        trylet client_fd os\FD = os\AcceptWithAddr(server_fd, make_mut_blob#(addr), 0), err:
            return 1
        trylet  n uint = os\SendTo(client_fd, gReply, 0), err:
            return 1
        trylet  n2 uint = os\SendTo(client_fd, "\r\n COOL\n\n\n", 0), err:
            return 1
        fmt\print#("Sent ", n, " bytes\n")
        tryset res = os\Close(client_fd), err:
            return 1

    tryset res = os\Shutdown(server_fd, os\SHUT.RDWR), err:
        return 1

    tryset res = os\Close(server_fd), err:
        return 1

    return 0