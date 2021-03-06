---------------------------------------------------------------------------
--
-- RISC-V Model
-- Based on the MIPS specification by Anthony Fox, University of Cambridge
--
-- Copyright (C) 2014, 2015 Anthony Fox, University of Cambridge
-- Copyright (C) 2014, 2015 Alexandre Joannou, University of Cambridge
-- Copyright (C) 2015-2017, SRI International.
--
-- This software was developed by SRI International and the University
-- of Cambridge Computer Laboratory under DARPA/AFRL contract
-- FA8750-11-C-0249 ("MRC2"), as part of the DARPA MRC research
-- programme, and under DARPA/AFRL contract FA8750-10-C-0237
-- ("CTSRD"), as part of the DARPA CRASH research programme.
--
-- See the LICENSE file for details.
--
-- For syntax highlighting, treat this file as Haskell source.
---------------------------------------------------------------------------


---------------------------------------------------------------------------
-- Basic types
---------------------------------------------------------------------------

type id       = bits(8)           -- max 256 cores
type reg      = bits(5)
type creg     = bits(12)

type byte     = bits(8)
type half     = bits(16)
type word     = bits(32)
type dword    = bits(64)

type fprnd    = bits(3)         -- rounding mode
type fpval    = bits(64)

type exc_code = bits(4)

-- instruction fields
type opcode   = bits(7)
type imm12    = bits(12)
type imm20    = bits(20)
type amo      = bits(1)

-- memory and caches

construct accessType { Read, Write, ReadWrite, Execute }
construct fetchType  { Instruction, Data }

type asid32   = bits(10)
type asid64   = bits(26)

-- RV64* base.

type regType  = dword
type vAddr    = dword
type pAddr    = dword

type pAddrIdx = bits(61)        -- raw index into physical memory
                                -- arranged in 8-byte blocks

-- Miscellaneous
exception UNDEFINED         :: string
exception INTERNAL_ERROR    :: string

---------------------------------------------------------------------------
-- Memory types for Load/Store instructions
---------------------------------------------------------------------------

type memWidth       = bits(3)

memWidth BYTE       = 0
memWidth HALFWORD   = 1
memWidth WORD       = 3
memWidth DOUBLEWORD = 7

---------------------------------------------------------------------------
-- Processor architecture
---------------------------------------------------------------------------

type arch_base = bits(2)

construct Architecture
{
  RV32I, RV64I, RV128I
}

arch_base archBase(a::Architecture) =
    match a
    { case RV32I      => 0
      case RV64I      => 2
      case RV128I     => 3
    }

Architecture architecture(ab::arch_base) =
    match ab
    { case 0          => RV32I
      case 2          => RV64I
      case 3          => RV128I
      case _          => #UNDEFINED("Unknown architecture: " : [[ab] :: nat])
    }

string archName(a::Architecture) =
    match a
    { case RV32I      => "RV32I"
      case RV64I      => "RV64I"
      case RV128I     => "RV128I"
    }

---------------------------------------------------------------------------
-- Privilege levels
---------------------------------------------------------------------------

type priv_level = bits(2)

construct Privilege
{ User
, Supervisor
, Hypervisor
, Machine
}

priv_level privLevel(p::Privilege) =
    match p
    { case User       => 0
      case Supervisor => 1
      case Hypervisor => 2
      case Machine    => 3
    }

Privilege privilege(p::priv_level) =
    match p
    { case 0          => User
      case 1          => Supervisor
      case 2          => Hypervisor
      case 3          => Machine
    }

string privName(p::Privilege) =
    match p
    { case User       => "U"
      case Supervisor => "S"
      case Hypervisor => "H"
      case Machine    => "M"
    }

---------------------------------------------------------------------------
-- Memory management and virtualization
---------------------------------------------------------------------------

type vm_mode    = bits(5)

construct VM_Mode
{ Mbare
, Mbb
, Mbbid
, Sv32
, Sv39
, Sv48
, Sv57
, Sv64
}

VM_Mode vmType(vm::vm_mode) =
    match vm
    { case  0     => Mbare
      case  1     => Mbb
      case  2     => Mbbid
      case  8     => Sv32
      case  9     => Sv39
      case 10     => Sv48
      case 11     => Sv57
      case 12     => Sv64
      case  _     => #UNDEFINED("Unknown address translation mode: " : [[vm]::nat])
    }

bool isValidVM(vm::vm_mode) =
    match vm
    { case 0 or 1 or 2 or 8 or 9 or 10 or 11 or 12 => true
      case _                                       => false
    }

vm_mode vmMode(vm::VM_Mode) =
    match vm
    { case Mbare  => 0
      case Mbb    => 1
      case Mbbid  => 2
      case Sv32   => 8
      case Sv39   => 9
      case Sv48   => 10
      case Sv57   => 11
      case Sv64   => 12
    }

string vmModeName(vm::VM_Mode) =
    match vm
    { case Mbare  => "Mbare"
      case Mbb    => "Mbb"
      case Mbbid  => "Mbbid"
      case Sv32   => "Sv32"
      case Sv39   => "Sv39"
      case Sv48   => "Sv48"
      case Sv57   => "Sv57"
      case Sv64   => "Sv64"
    }

---------------------------------------------------------------------------
-- Extension Context Status
---------------------------------------------------------------------------

type ext_status = bits(2)

construct ExtStatus
{ Off
, Initial
, Clean
, Dirty
}

ext_status ext_status(e::ExtStatus) =
    match e
    { case Off      => 0
      case Initial  => 1
      case Clean    => 2
      case Dirty    => 3
    }

ExtStatus extStatus(e::ext_status) =
    match e
    { case 0        => Off
      case 1        => Initial
      case 2        => Clean
      case 3        => Dirty
    }

string extStatusName(e::ExtStatus) =
    match e
    { case Off      => "Off"
      case Initial  => "Initial"
      case Clean    => "Clean"
      case Dirty    => "Dirty"
    }

---------------------------------------------------------------------------
-- Exceptions and Interrupts
---------------------------------------------------------------------------

construct InterruptType
{ I_U_Software
, I_S_Software
, I_H_Software
, I_M_Software
, I_U_Timer
, I_S_Timer
, I_H_Timer
, I_M_Timer
, I_U_External
, I_S_External
, I_H_External
, I_M_External
}

exc_code interruptIndex(i::InterruptType) =
    match i
    { case I_U_Software => 0x0
      case I_S_Software => 0x1
      case I_H_Software => 0x2
      case I_M_Software => 0x3

      case I_U_Timer    => 0x4
      case I_S_Timer    => 0x5
      case I_H_Timer    => 0x6
      case I_M_Timer    => 0x7

      case I_U_External => 0x8
      case I_S_External => 0x9
      case I_H_External => 0xa
      case I_M_External => 0xb
    }

construct ExceptionType
{ E_Fetch_Misaligned
, E_Fetch_Fault
, E_Illegal_Instr
, E_Breakpoint
, E_Load_Fault
, E_AMO_Misaligned
, E_Store_AMO_Fault
, E_Env_Call
, E_Fetch_Page_Fault
, E_Load_Page_Fault
, E_Store_Page_Fault
}

exc_code excCode(e::ExceptionType) =
    match e
    { case E_Fetch_Misaligned   => 0x0
      case E_Fetch_Fault        => 0x1
      case E_Illegal_Instr      => 0x2
      case E_Breakpoint         => 0x3
      -- an implementation could use 0x4 for E_Load_Access if needed
      case E_Load_Fault         => 0x5
      case E_AMO_Misaligned     => 0x6
      case E_Store_AMO_Fault    => 0x7

      case E_Env_Call           => 0x8
      case E_Fetch_Page_Fault   => 0xc
      case E_Load_Page_Fault    => 0xd
      case E_Store_Page_Fault   => 0xf
    }

ExceptionType excType(e::exc_code) =
    match e
    { case 0x0 => E_Fetch_Misaligned
      case 0x1 => E_Fetch_Fault
      case 0x2 => E_Illegal_Instr
      case 0x3 => E_Breakpoint

      case 0x5 => E_Load_Fault
      case 0x6 => E_AMO_Misaligned
      case 0x7 => E_Store_AMO_Fault

      case 0x8 => E_Env_Call
      case 0xc => E_Fetch_Page_Fault
      case 0xd => E_Load_Page_Fault
      case 0xf => E_Store_Page_Fault

      case _   => #UNDEFINED("Unknown exception: " : [[e]::nat])
    }

string excName(e::ExceptionType) =
    match e
    { case E_Fetch_Misaligned   => "MISALIGNED_FETCH"
      case E_Fetch_Fault        => "FAULT_FETCH"
      case E_Illegal_Instr      => "ILLEGAL_INSTRUCTION"
      case E_Breakpoint         => "BREAKPOINT"

      case E_Load_Fault         => "FAULT_LOAD"
      case E_AMO_Misaligned     => "MISALIGNED_AMO"
      case E_Store_AMO_Fault    => "FAULT_STORE_AMO"

      case E_Env_Call           => "EnvCall"
      case E_Fetch_Page_Fault   => "FETCH_PAGE_FAULT"
      case E_Load_Page_Fault    => "LOAD_PAGE_FAULT"
      case E_Store_Page_Fault   => "STORE_PAGE_FAULT"
    }

---------------------------------------------------------------------------
-- Control and Status Registers (CSRs)
---------------------------------------------------------------------------

-- Machine state projections
--
-- There are two kinds of projections needed: (i) from machine-level
-- views to views from lower privilege levels, and (ii) from the
-- 64-bit implementation width to 32-bit views.  We implement views as
-- a projection of kind (i) followed by that of kind (ii).
--
-- Each register definition is followed by any custom projections
-- needed.

-- TODO: writes to WPRI fields are not currently checked for
-- preservation; adding checks would provide useful diagnostics.

-- Machine-Level CSRs

register misa :: regType        -- Machine ISA
{ 63-62 : ArchBase  -- base architecture, machine mode on reset
,    23 : X         -- non-standard extensions
,    20 : U         -- user-mode
,    18 : S         -- supervisor-mode
,    13 : N         -- user-level interrupts
,    12 : M         -- integer multiply/divide
,     8 : I         -- integer base ISA support
,     5 : F         -- single-precision floating-point
,     3 : D         -- double-precision floating-point
,     0 : A         -- atomics
}

word  isa_to_32(v::dword) = [v<63:62> : 0x0`4  : v<25:0>]
dword isa_of_32(v::word)  = [v<31:30> : 0x0`36 : v<25:0>]

regType MVENDORID = 0
regType MARCHID   = 0
regType MIMPID    = 0

register mstatus :: regType     -- Machine Status
{    63 : M_SD      -- extended context dirty status
, 28-24 : M_VM      -- memory management and virtualization
,    19 : M_MXR     -- make executable readable
,    18 : M_PUM     -- protect user memory
,    17 : M_MPRV    -- load/store memory privilege
, 16-15 : M_XS      -- extension context status
, 14-13 : M_FS      -- floating-point context status
, 12-11 : M_MPP     -- per-privilege pre-trap privilege modes
,  10-9 : M_HPP
,     8 : M_SPP
,     7 : M_MPIE    -- per-privilege pre-trap interrupt enables
,     6 : M_HPIE
,     5 : M_SPIE
,     4 : M_UPIE
,     3 : M_MIE     -- per-privilege interrupt enables
,     2 : M_HIE
,     1 : M_SIE
,     0 : M_UIE
}

word  status_to_32(v::dword) = [v<63>]::bits(1) : 0x0`2  : v<28:0>
dword status_of_32(v::word)  = [v<31>]::bits(1) : 0x0`32 : v<30:0>

register medeleg :: regType     -- Exception Trap Delegation
{    15 : M_Store_Page_Fault
,    14 : M_E_Deleg_unused_14
,    13 : M_Load_Page_Fault
,    12 : M_Fetch_Page_Fault
,    11 : M_MEnvCall     
,    10 : M_HEnvCall
,     9 : M_SEnvCall
,     8 : M_UEnvCall
,     7 : M_SAMO_Access
,     6 : M_SAMO_Addr
,     5 : M_Load_Access
,     4 : M_Load_Addr_Align
,     3 : M_Breakpoint
,     2 : M_Illegal_Instr
,     1 : M_Fetch_Fault
,     0 : M_Fetch_Addr_Align
}

register mideleg :: regType     -- Interrupt Trap Delegation
{    11 : M_MEIP   -- external interrupts
,    10 : M_HEIP
,     9 : M_SEIP
,     8 : M_UEIP
,     7 : M_MTIP   -- timer interrupts
,     6 : M_HTIP
,     5 : M_STIP
,     4 : M_UTIP
,     3 : M_MSIP   -- software interrupts
,     2 : M_HSIP
,     1 : M_SSIP
,     0 : M_USIP
}

register mip :: regType         -- Interrupt Pending
{    11 : M_MEIP   -- external interrupts
,    10 : M_HEIP
,     9 : M_SEIP
,     8 : M_UEIP
,     7 : M_MTIP   -- timer interrupts
,     6 : M_HTIP
,     5 : M_STIP
,     4 : M_UTIP
,     3 : M_MSIP   -- software interrupts
,     2 : M_HSIP
,     1 : M_SSIP
,     0 : M_USIP
}

word  ip_to_32(v::dword) = v<31:0>
dword ip_of_32(v::word)  = ZeroExtend(v<11:0>)

register mie :: regType         -- Interrupt Enable
{    11 : M_MEIE    -- external interrupts
,    10 : M_HEIE
,     9 : M_SEIE
,     8 : M_UEIE
,     7 : M_MTIE    -- timer interrupts
,     6 : M_HTIE
,     5 : M_STIE
,     4 : M_UTIE
,     3 : M_MSIE    -- software interrupts
,     2 : M_HSIE
,     1 : M_SSIE
,     0 : M_USIE
}

word  ie_to_32(v::dword) = v<31:0>
dword ie_of_32(v::word)  = ZeroExtend(v<31:0>)

register mcounteren :: regType  -- Machine Counter-Enable
{     2 : M_IR      -- instructions retired
,     1 : M_TM      -- time
,     0 : M_CY      -- cycles
}

register mcause :: regType      -- Trap Cause
{    63 : M_Intr
,  62-0 : M_ExcCause
}

word  cause_to_32(v::dword) = [v<63>]::bits(1) : v<30:0>
dword cause_of_32(v::word)  = [v<31>]::bits(1) : 0x0`32 : v<30:0>

record MachineCSR
{ misa          :: misa         -- information registers
  mvendorid     :: regType
  marchid       :: regType
  mimpid        :: regType
  mhartid       :: regType

  mstatus       :: mstatus      -- trap setup
  medeleg       :: medeleg
  mideleg       :: mideleg
  mie           :: mie
  mtvec         :: regType

  mscratch      :: regType      -- trap handling
  mepc          :: regType
  mcause        :: mcause
  mbadaddr      :: regType
  mip           :: mip

  pmpcfg0       :: regType      -- new csr protection registers (WIP)
  pmpcfg1       :: regType
  pmpcfg2       :: regType
  pmpcfg3       :: regType
  pmpaddr0      :: regType
  pmpaddr1      :: regType
  pmpaddr2      :: regType
  pmpaddr3      :: regType
  pmpaddr4      :: regType
  pmpaddr5      :: regType
  pmpaddr6      :: regType
  pmpaddr7      :: regType
  pmpaddr8      :: regType
  pmpaddr9      :: regType
  pmpaddrA      :: regType
  pmpaddrB      :: regType
  pmpaddrC      :: regType
  pmpaddrD      :: regType
  pmpaddrE      :: regType
  pmpaddrF      :: regType

  mcycle        :: regType      -- timers and counters
  mtime         :: regType
  minstret      :: regType

  mucounteren   :: mcounteren   -- counter setup
  mscounteren   :: mcounteren
  mhcounteren   :: mcounteren

  mucycle_delta     :: regType  -- counter-deltas
  mutime_delta      :: regType
  muinstret_delta   :: regType

  mscycle_delta     :: regType
  mstime_delta      :: regType
  msinstret_delta   :: regType
}

-- Hypervisor-Level CSRs

record HypervisorCSR
{ hstatus       :: mstatus      -- trap setup
  hedeleg       :: regType
  hideleg       :: regType
  hie           :: regType
  htvec         :: regType

  hscratch      :: regType      -- trap handling
  hepc          :: regType
  hcause        :: mcause
  hbadaddr      :: regType
}

-- Supervisor-Level CSRs

register sstatus :: regType
{    63 : S_SD      -- extended context dirty status
,    18 : S_PUM     -- protect user memory
, 16-15 : S_XS      -- extension context status
, 14-13 : S_FS      -- floating-point context status
,     8 : S_SPP     -- pre-trap privilege modes
,     5 : S_SPIE    -- pre-trap interrupt enables
,     4 : S_UPIE
,     1 : S_SIE     -- interrupt-enables
,     0 : S_UIE
}

sstatus to_sstatus(v::mstatus) =
{ var s = sstatus(0)
; s.S_SD    <- v.M_SD
; s.S_PUM   <- v.M_PUM
; s.S_XS    <- v.M_XS
; s.S_FS    <- v.M_FS
; s.S_SPP   <- v.M_SPP
; s.S_SPIE  <- v.M_SPIE
; s.S_UPIE  <- v.M_UPIE
; s.S_SIE   <- v.M_SIE
; s.S_UIE   <- v.M_UIE
; s
}

mstatus of_sstatus(v::sstatus, orig::mstatus) =
{ var m = mstatus(&orig)
; m.M_SD    <- v.S_SD
; m.M_PUM   <- v.S_PUM
; m.M_XS    <- v.S_XS
; m.M_FS    <- v.S_FS
; m.M_SPP   <- v.S_SPP
; m.M_SPIE  <- v.S_SPIE
; m.M_UPIE  <- v.S_UPIE
; m.M_SIE   <- v.S_SIE
; m.M_UIE   <- v.S_UIE
; m
}

register sedeleg :: regType     -- Exception Trap Delegation
{     9 : S_SEnvCall
,     8 : S_UEnvCall
,     7 : S_SAMO_Access
,     6 : S_SAMO_Addr
,     5 : S_Load_Access
,     4 : S_Load_Addr_Align
,     3 : S_Breakpoint
,     2 : S_Illegal_Instr
,     1 : S_Fetch_Fault
,     0 : S_Fetch_Addr_Align
}

register sideleg :: regType     -- Interrupt Trap Delegation
{     9 : S_SEIP   -- external interrupts
,     8 : S_UEIP
,     5 : S_STIP   -- timer interrupts
,     4 : S_UTIP
,     1 : S_SSIP   -- software interrupts
,     0 : S_USIP
}

register sip :: regType         -- Interrupt Pending
{     9 : S_SEIP   -- external interrupts
,     8 : S_UEIP
,     5 : S_STIP   -- timer interrupts
,     4 : S_UTIP
,     1 : S_SSIP   -- software interrupts
,     0 : S_USIP
}

-- TODO: expose other interrupt bits in sip/sie via checking for
-- delegation in mideleg.

sip to_sip(v::mip) =
{ var s = sip(0)
; s.S_SEIP  <- v.M_SEIP
; s.S_UEIP  <- v.M_UEIP
; s.S_STIP  <- v.M_STIP
; s.S_UTIP  <- v.M_UTIP
; s.S_SSIP  <- v.M_SSIP
; s.S_USIP  <- v.M_USIP
; s
}

mip of_sip(v::sip, orig::mip) =
{ var m = mip(&orig)
; m.M_SEIP  <- v.S_SEIP
; m.M_UEIP  <- v.S_UEIP
; m.M_STIP  <- v.S_STIP
; m.M_UTIP  <- v.S_UTIP
; m.M_SSIP  <- v.S_SSIP
; m.M_USIP  <- v.S_USIP
; m
}

register sie :: regType         -- Interrupt Enable
{     9 : S_SEIE    -- external interrupts
,     8 : S_UEIE
,     5 : S_STIE    -- timer interrupts
,     4 : S_UTIE
,     1 : S_SSIE    -- software interrupts
,     0 : S_USIE
}

sie to_sie(v::mie) =
{ var s = sie(0)
; s.S_SEIE  <- v.M_SEIE
; s.S_UEIE  <- v.M_UEIE
; s.S_STIE  <- v.M_STIE
; s.S_UTIE  <- v.M_UTIE
; s.S_SSIE  <- v.M_SSIE
; s.S_USIE  <- v.M_USIE
; s
}

mie of_sie(v::sie, orig::mie) =
{ var m = mie(&orig)
; m.M_SEIE  <- v.S_SEIE
; m.M_UEIE  <- v.S_UEIE
; m.M_STIE  <- v.S_STIE
; m.M_UTIE  <- v.S_UTIE
; m.M_SSIE  <- v.S_SSIE
; m.M_USIE  <- v.S_USIE
; m
}

register sptbr32 :: word
{ 31-22 : ASID_32
, 21-0  : PPN_32
}

register sptbr64 :: regType
{ 63-38 : ASID_64
, 37-0  : PPN_64
}

record SupervisorCSR
{ sstatus       :: sstatus      -- trap setup
  sedeleg       :: sedeleg
  sideleg       :: sideleg
  stvec         :: regType

  sscratch      :: regType      -- trap handling
  sepc          :: regType
  scause        :: mcause
  sbadaddr      :: regType
  sip           :: sip

  sptbr         :: regType      -- memory protection and translation
}

-- User-Level CSRs

-- floating point control and status

register FPCSR :: word          -- 32-bit control register
{ 7-5 : FRM         -- dynamic rounding mode
                    -- exception flags
,   4 : NV          --     invalid operation
,   3 : DZ          --     divide by zero
,   2 : OF          --     overflow
,   1 : UF          --     underflow
,   0 : NX          --     inexact
}

-- FIXME: These fields are not specified in the 1.9 privileged spec.
-- SD, XS, FS, if exposed, could enable user-level threads.  But their
-- handling will be complicated due to distinguishing user-updates
-- from physical-register updates.

register ustatus :: regType     -- Status
{     4 : U_PIE     -- pre-trap interrupt enable
,     0 : U_IE      -- interrupt-enable
}

ustatus to_ustatus(v::mstatus) =
{ var u = ustatus(0)
; u.U_PIE   <- v.M_UPIE
; u.U_IE    <- v.M_UIE
; u
}

mstatus of_ustatus(v::ustatus, orig::mstatus) =
{ var m = mstatus(&orig)
; m.M_UPIE  <- v.U_PIE
; m.M_UIE   <- v.U_IE
; m
}

register uip :: regType         -- Interrupt Pending
{     8 : U_EIP     -- external interrupts
,     4 : U_TIP     -- timer interrupts
,     0 : U_SIP     -- software interrupts
}

uip to_uip(v::mip) =
{ var s = uip(0)
; s.U_EIP   <- v.M_UEIP
; s.U_TIP   <- v.M_UTIP
; s.U_SIP   <- v.M_USIP
; s
}

mip of_uip(v::uip, orig::mip) =
{ var m = mip(&orig)
; m.M_UEIP  <- v.U_EIP
; m.M_UTIP  <- v.U_TIP
; m.M_USIP  <- v.U_SIP
; m
}

register uie :: regType         -- Interrupt Enable
{     8 : U_EIE     -- external interrupts
,     4 : U_TIE     -- timer interrupts
,     0 : U_SIE     -- software interrupts
}

uie to_uie(v::mie) =
{ var s = uie(0)
; s.U_EIE   <- v.M_UEIE
; s.U_TIE   <- v.M_UTIE
; s.U_SIE   <- v.M_USIE
; s
}

mie of_uie(v::uie, orig::mie) =
{ var m = mie(&orig)
; m.M_UEIE  <- v.U_EIE
; m.M_UTIE  <- v.U_TIE
; m.M_USIE  <- v.U_SIE
; m
}

record UserCSR
{ utvec         :: regType      -- trap setup

  uscratch      :: regType      -- trap handling
  uepc          :: regType
  ucause        :: mcause
  ubadaddr      :: regType

  fpcsr         :: FPCSR        -- floating-point
}

-- update utilities

bool isValidHPP(p::bits(2)) = privilege(p) != Machine

mstatus update_mstatus(orig::mstatus, v::mstatus) =
{ var m = orig
-- interrupt enables
; m.M_UIE   <- v.M_UIE
; m.M_SIE   <- v.M_SIE
; m.M_HIE   <- v.M_HIE
; m.M_MIE   <- v.M_MIE
-- pre-trap interrupt enables
; m.M_UPIE  <- v.M_UPIE
; m.M_SPIE  <- v.M_SPIE
; m.M_HPIE  <- v.M_HPIE
; m.M_MPIE  <- v.M_MPIE
-- pre-trap privilege modes
; m.M_SPP   <- v.M_SPP
; m.M_HPP   <- if isValidHPP(v.M_HPP) then v.M_HPP else orig.M_HPP
; m.M_MPP   <- v.M_MPP

-- update extension context status
; m.M_FS    <- v.M_FS
; m.M_XS    <- v.M_XS
-- update read-only field appropriately
; m.M_SD    <- extStatus(v.M_XS) == Dirty or extStatus(v.M_FS) == Dirty

-- memory privilege settings
; m.M_MPRV  <- v.M_MPRV
; m.M_PUM   <- v.M_PUM
; m.M_MXR   <- v.M_MXR

-- ensure a valid address translation mode
; when isValidVM(v.M_VM)
  do m.M_VM <- v.M_VM

; m
}

-- utilities for privilege transitions

mstatus menter(v::mstatus, p::Privilege) =
{ var m = v
; m.M_MPIE <- match p
              { case User       => m.M_UIE
                case Supervisor => m.M_SIE
                case Hypervisor => m.M_HIE
                case Machine    => m.M_MIE
              }
; m.M_MPP <- privLevel(p)
; m.M_MIE <- false
; m
}

mstatus henter(v::mstatus, p::Privilege) =
{ var m = v
; m.M_HPIE <- match p
              { case User       => m.M_UIE
                case Supervisor => m.M_SIE
                case Hypervisor => m.M_HIE
                case Machine    => #INTERNAL_ERROR("Invalid privilege for henter")
              }
; m.M_HPP <- privLevel(p)
; m.M_HIE <- false
; m
}

mstatus senter(v::mstatus, p::Privilege) =
{ var m = v
; match p
  { case User       => { m.M_SPIE <- m.M_UIE
                       ; m.M_SPP  <- false
                       }
    case Supervisor => { m.M_SPIE <- m.M_SIE
                       ; m.M_SPP  <- true
                       }
    case _          => #INTERNAL_ERROR("Invalid privilege for senter")
  }
; m.M_SIE <- false
; m
}

mstatus uenter(v::mstatus, p::Privilege) =
{ var m = v
; m.M_UPIE <- match p
              { case User       => m.M_UIE
                case _          => #INTERNAL_ERROR("Invalid privilege for uenter")
              }
; m.M_UIE <- false
; m
}

mstatus mret(v::mstatus) =
{ var m = v
; match privilege(m.M_MPP)
  { case User       => m.M_UIE  <- m.M_MPIE
    case Supervisor => m.M_SIE  <- m.M_MPIE
    case Hypervisor => m.M_HIE  <- m.M_MPIE
    case Machine    => m.M_MIE  <- m.M_MPIE
  }
; m.M_MPP  <- privLevel(User)
; m.M_MPIE <- true
; m
}

mstatus hret(v::mstatus) =
{ var m = v
; match privilege(m.M_HPP)
  { case User       => m.M_UIE  <- m.M_HPIE
    case Supervisor => m.M_SIE  <- m.M_HPIE
    case Hypervisor => m.M_HIE  <- m.M_HPIE
    case _          => #INTERNAL_ERROR("Invalid mstatus for HRET")
  }
; m.M_HPP  <- privLevel(User)
; m.M_HPIE <- true
; m
}

mstatus sret(v::mstatus) =
{ var m = v
; match m.M_SPP
  { case false      => m.M_UIE  <- m.M_SPIE
    case true       => m.M_SIE  <- m.M_SPIE
  }
; m.M_SPP  <- false
; m.M_SPIE <- true
; m
}

mstatus uret(v::mstatus) =
{ var m = v
; m.M_UIE  <- m.M_UPIE
; m.M_UPIE <- true
; m
}

---------------------------------------------------------------------------
-- Instruction fetch state
---------------------------------------------------------------------------

record SynchronousException
{ trap            :: ExceptionType
  badaddr         :: vAddr option
}

construct instrResult
{ Trap            :: SynchronousException
, Uret
, Sret
, Hret
, Mret
, BranchTo        :: regType
}

type FetchState = instrResult option

---------------------------------------------------------------------------
-- Register state space
---------------------------------------------------------------------------

-- Each register state is local to a core.

type RegFile    = reg  -> regType

declare
{ clock         :: regType                      -- global clock and counters

  c_instret     :: id -> regType                -- per-core counters
  c_cycles      :: id -> regType

  c_gpr         :: id -> RegFile                -- general purpose registers
  c_fpr         :: id -> RegFile                -- floating-point registers

  c_PC          :: id -> regType                -- program counter

  c_UCSR        :: id -> UserCSR                -- user-level CSRs
  c_SCSR        :: id -> SupervisorCSR          -- supervisor-level CSRs
  c_HCSR        :: id -> HypervisorCSR          -- hypervisor-level CSRs
  c_MCSR        :: id -> MachineCSR             -- machine-level CSRs

  c_privilege   :: id -> Privilege              -- current execution context privilege

  -- interpreter execution context
  c_NextFetch   :: id -> FetchState
  c_ReserveLoad :: id -> vAddr option           -- load reservation for LL/SC
  c_ExitCode    :: id -> regType                -- derived from Berkeley HTIF
}

-- Number of cores
declare totalCore :: nat

-- ID of the core executing current instruction
declare procID :: id

unit scheduleCore(id :: nat) =
    when id < totalCore
    do procID <- [id]

-- The following components provide read/write access to state of the
-- core whose id equals procID.  For example, writing "gpr(r)" refers
-- general purpose register "r" in the core whose id equals procID.

component gpr(n::reg) :: regType
{ value        = { m = c_gpr(procID); m(n) }
  assign value = { var m = c_gpr(procID)
                 ; m(n) <- value
                 ; c_gpr(procID) <- m
                 }
}

component fcsr :: FPCSR
{ value        = c_UCSR(procID).fpcsr
  assign value = { c_UCSR(procID).fpcsr         <- value
                 ; c_MCSR(procID).mstatus.M_FS  <- ext_status(Dirty)
                 ; c_MCSR(procID).mstatus.M_SD  <- true
                 }
}

component fpr(n::reg) :: regType
{ value        = { m = c_fpr(procID); m(n) }
  assign value = { var m = c_fpr(procID)
                 ; m(n) <- value
                 ; c_fpr(procID) <- m
                 }
}

component PC :: regType
{ value        = c_PC(procID)
  assign value = c_PC(procID) <- value
}

component UCSR :: UserCSR
{ value        = c_UCSR(procID)
  assign value = c_UCSR(procID) <- value
}

component SCSR :: SupervisorCSR
{ value        = c_SCSR(procID)
  assign value = c_SCSR(procID) <- value
}

component HCSR :: HypervisorCSR
{ value        = c_HCSR(procID)
  assign value = c_HCSR(procID) <- value
}

component MCSR :: MachineCSR
{ value        = c_MCSR(procID)
  assign value = c_MCSR(procID) <- value
}

component NextFetch :: FetchState
{ value        = c_NextFetch(procID)
  assign value = c_NextFetch(procID) <- value
}

component ReserveLoad :: vAddr option
{ value        = c_ReserveLoad(procID)
  assign value = c_ReserveLoad(procID) <- value
}

component ExitCode :: regType
{ value        = c_ExitCode(procID)
  assign value = c_ExitCode(procID) <- value
}

component curPrivilege :: Privilege
{ value        = c_privilege(procID)
  assign value = c_privilege(procID) <- value
}

-- machine state utilities

Architecture curArch() =
    architecture(MCSR.misa.ArchBase)

bool in32BitMode() =
    curArch() == RV32I

bool isFPEnabled() =
    MCSR.misa.F

asid32 curAsid32() =
    sptbr32(SCSR.sptbr<31:0>).ASID_32

asid64 curAsid64() =
    sptbr64(SCSR.sptbr).ASID_64

---------------------------------------------------------------------------
-- Floating Point
---------------------------------------------------------------------------

-- Rounding

construct Rounding
{ RNE, RTZ, RDN, RUP, RMM, RDYN }

-- instruction rounding mode
Rounding option rnd_mode_static(rnd::fprnd) =
    match rnd
    { case 0          => Some(RNE)
      case 1          => Some(RTZ)
      case 2          => Some(RDN)
      case 3          => Some(RUP)
      case 4          => Some(RMM)
      case 7          => Some(RDYN)     -- from rounding mode register
      case _          => None
    }

-- dynamic rounding mode
Rounding option rnd_mode_dynamic(rnd::fprnd) =
    match rnd
    { case 0          => Some(RNE)
      case 1          => Some(RTZ)
      case 2          => Some(RDN)
      case 3          => Some(RUP)
      case 4          => Some(RMM)
      case _          => None
    }

-- currently implemented rounding modes
ieee_rounding option l3round(rnd::Rounding) =
    match rnd
    { case RNE        => Some(roundTiesToEven)
      case RTZ        => Some(roundTowardZero)
      case RDN        => Some(roundTowardNegative)
      case RUP        => Some(roundTowardPositive)
      case RMM        => None  -- roundTiesToMaxMagnitude not in L3
      case RDYN       => None  -- invalid
    }

-- composed rounding mode
ieee_rounding option round(rnd::fprnd) =
    match rnd_mode_static(rnd)
    { case Some(RDYN) => match rnd_mode_dynamic(fcsr.FRM)
                         { case Some(frm) => l3round(frm)
                           case None      => None
                         }
      case Some(frm)  => l3round(frm)
      case None       => None
    }

-- NaNs

bits(32) RV32_CanonicalNan = 0x7fc00000
bits(64) RV64_CanonicalNan = 0x7ff8000000000000

-- Classification

bool FP32_IsSignalingNan(x::bits(32)) =
    (x<30:23> == 0xff`8)   and x<22> == false and (x<21:0> != 0x0`22)

bool FP64_IsSignalingNan(x::bits(64)) =
    (x<62:52> == 0x7ff`11) and x<51> == false and (x<50:0> != 0x0`51)

bool FP32_Sign(x::bits(32)) = x<31>
bool FP64_Sign(x::bits(64)) = x<63>

-- setting exception flags

unit setFP_Invalid() =
    fcsr.NV <- true

unit setFP_DivZero() =
    fcsr.DZ <- true

unit setFP_Overflow() =
    fcsr.OF <- true

unit setFP_Underflow() =
    fcsr.OF <- true

unit setFP_Inexact() =
    fcsr.OF <- true

---------------------------------------------------------------------------
-- CSR Register address map
---------------------------------------------------------------------------

-- CSR access control

type csrRW    = bits(2)         -- read/write check
type csrPR    = bits(2)         -- privilege check

csrRW csrRW(csr::creg)  = csr<11:10>
csrPR csrPR(csr::creg)  = csr<9:8>

-- this only checks register-level access.  some registers have
-- additional bit-specific read/write controls.
bool check_CSR_access(rw::csrRW, pr::csrPR, p::Privilege, a::accessType) =
    (a == Read or rw != 0b11) and (privLevel(p) >=+ pr)

bool is_CSR_defined(csr::creg) =
    -- user-mode
    csr == 0x000  or  csr == 0x004 or csr == 0x005
 or (csr >= 0x001 and csr <= 0x003 and isFPEnabled())
 or (csr >= 0x040 and csr <= 0x044)
 or (csr == 0xC00 and c_MCSR(procID).mucounteren.M_CY)
 or (csr == 0xC01 and c_MCSR(procID).mucounteren.M_TM)
 or (csr == 0xC02 and c_MCSR(procID).mucounteren.M_IR)
 or ((   (csr == 0xC80 and c_MCSR(procID).mucounteren.M_CY)
      or (csr == 0xC81 and c_MCSR(procID).mucounteren.M_TM)
      or (csr == 0xC82 and c_MCSR(procID).mucounteren.M_IR)) and in32BitMode())

    -- supervisor-mode
 or (csr >= 0x100 and csr <= 0x105 and csr != 0x101)
 or (csr >= 0x140 and csr <= 0x144)
 or (csr == 0x180)
 or (csr == 0xD00 and c_MCSR(procID).mscounteren.M_CY)
 or (csr == 0xD01 and c_MCSR(procID).mscounteren.M_TM)
 or (csr == 0xD02 and c_MCSR(procID).mscounteren.M_IR)
 or ((   (csr == 0xD80 and c_MCSR(procID).mucounteren.M_CY)
      or (csr == 0xD81 and c_MCSR(procID).mucounteren.M_TM)
      or (csr == 0xD82 and c_MCSR(procID).mucounteren.M_IR)) and in32BitMode())

    -- machine-mode
 or (csr >= 0x300 and csr <= 0x305 and csr != 0x301)
 or (csr >= 0x310 and csr <= 0x312)
 or (csr >= 0x340 and csr <= 0x344)
 or (csr >= 0x3A0 and csr <= 0x3A3)
 or (csr >= 0x3B0 and csr <= 0x3BF)
 or (csr >= 0xF00 and csr <= 0xF02)
 or (csr >= 0xF10 and csr <= 0xF14)
 or (csr >= 0xF80 and csr <= 0xF82 and in32BitMode())

 or (csr >= 0x700 and csr <= 0x702)
 or (csr >= 0x704 and csr <= 0x706)
 or (csr >= 0x708 and csr <= 0x70A)

 or ((   (csr >= 0x780 and csr <= 0x782)
      or (csr >= 0x784 and csr <= 0x786)
      or (csr >= 0x788 and csr <= 0x78A)) and in32BitMode())

component CSRMap(csr::creg) :: regType
{ value =
  -- Implementation note: in 32-bit mode, 32-bit CSR values are
  -- sign-extended so that the sign-bit is preserved.
      match csr, in32BitMode()
      { -- user trap setup
        case 0x000, false   => &to_ustatus(c_MCSR(procID).mstatus)
        case 0x000, true    => SignExtend(status_to_32(&to_ustatus(c_MCSR(procID).mstatus)))
        case 0x004, false   => &to_uie(c_MCSR(procID).mie)
        case 0x004, true    => SignExtend(ie_to_32(&to_uie(c_MCSR(procID).mie)))
        case 0x005, _       => c_UCSR(procID).utvec

        -- user trap handling
        case 0x040, _       => c_UCSR(procID).uscratch
        case 0x041, _       => c_UCSR(procID).uepc
        case 0x042, false   => c_UCSR(procID).&ucause
        case 0x042, true    => SignExtend(cause_to_32(c_UCSR(procID).&ucause))
        case 0x043, _       => c_UCSR(procID).ubadaddr
        case 0x044, false   => &to_uip(c_MCSR(procID).mip)
        case 0x044, true    => SignExtend(&to_uip(c_MCSR(procID).mip))

        -- user floating-point context
        case 0x001, _       => ZeroExtend(c_UCSR(procID).&fpcsr<4:0>)
        case 0x002, _       => ZeroExtend(c_UCSR(procID).fpcsr.FRM)
        case 0x003, _       => ZeroExtend(c_UCSR(procID).&fpcsr<7:0>)

        -- user counter/timers
        case 0xC00, false   =>             c_MCSR(procID).mcycle   + c_MCSR(procID).mucycle_delta
        case 0xC00, true    => SignExtend((c_MCSR(procID).mcycle   + c_MCSR(procID).mucycle_delta)<31:0>)
        case 0xC01, false   =>             c_MCSR(procID).mtime    + c_MCSR(procID).mutime_delta
        case 0xC01, true    => SignExtend((c_MCSR(procID).mtime    + c_MCSR(procID).mutime_delta)<31:0>)
        case 0xC02, false   =>             c_MCSR(procID).minstret + c_MCSR(procID).muinstret_delta
        case 0xC02, true    => SignExtend((c_MCSR(procID).minstret + c_MCSR(procID).muinstret_delta)<31:0>)
        case 0xC80, true    => SignExtend((c_MCSR(procID).mcycle   + c_MCSR(procID).mucycle_delta)<63:32>)
        case 0xC81, true    => SignExtend((c_MCSR(procID).mtime    + c_MCSR(procID).mutime_delta)<63:32>)
        case 0xC82, true    => SignExtend((c_MCSR(procID).minstret + c_MCSR(procID).muinstret_delta)<63:32>)

        -- supervisor trap setup
        case 0x100, false   => &to_sstatus(c_MCSR(procID).mstatus)
        case 0x100, true    => SignExtend(status_to_32(&to_sstatus(c_MCSR(procID).mstatus)))
        case 0x102, _       => c_SCSR(procID).&sedeleg
        case 0x103, _       => c_SCSR(procID).&sideleg
        case 0x104, false   => &to_sie(c_MCSR(procID).mie)
        case 0x104, true    => SignExtend(ie_to_32(&to_uie(c_MCSR(procID).mie)))
        case 0x105, _       => c_SCSR(procID).stvec

        -- supervisor trap handling
        case 0x140, _       => c_SCSR(procID).sscratch
        case 0x141, _       => c_SCSR(procID).sepc
        case 0x142, false   => c_SCSR(procID).&scause
        case 0x142, true    => SignExtend(cause_to_32(c_SCSR(procID).&scause))
        case 0x143, _       => c_SCSR(procID).sbadaddr
        case 0x144, false   => &to_sip(c_MCSR(procID).mip)
        case 0x144, true    => SignExtend(ip_to_32(&to_sip(c_MCSR(procID).mip)))

        -- supervisor protection and translation
        case 0x180, _       => c_SCSR(procID).sptbr

        -- supervisor counter/timers
        case 0xD00, false   =>             c_MCSR(procID).mcycle   + c_MCSR(procID).mscycle_delta
        case 0xD00, true    => SignExtend((c_MCSR(procID).mcycle   + c_MCSR(procID).mscycle_delta)<31:0>)
        case 0xD01, false   =>             c_MCSR(procID).mtime    + c_MCSR(procID).mstime_delta
        case 0xD01, true    => SignExtend((c_MCSR(procID).mtime    + c_MCSR(procID).mstime_delta)<31:0>)
        case 0xD02, false   =>             c_MCSR(procID).minstret + c_MCSR(procID).msinstret_delta
        case 0xD02, true    => SignExtend((c_MCSR(procID).minstret + c_MCSR(procID).msinstret_delta)<31:0>)
        case 0xD80, true    => SignExtend((c_MCSR(procID).mcycle   + c_MCSR(procID).mscycle_delta)<63:32>)
        case 0xD81, true    => SignExtend((c_MCSR(procID).mtime    + c_MCSR(procID).mstime_delta)<63:32>)
        case 0xD82, true    => SignExtend((c_MCSR(procID).minstret + c_MCSR(procID).msinstret_delta)<63:32>)

        -- Leave hypervisor CSRs for later.

        -- machine information registers
        case 0xF10, false   => c_MCSR(procID).&misa
        case 0xF10, true    => SignExtend(isa_to_32(c_MCSR(procID).&misa))
        case 0xF11, _       => c_MCSR(procID).mvendorid
        case 0xF12, _       => c_MCSR(procID).marchid
        case 0xF13, _       => c_MCSR(procID).mimpid
        case 0xF14, _       => c_MCSR(procID).mhartid

        -- machine trap setup
        case 0x300, false   => c_MCSR(procID).&mstatus
        case 0x300, true    => SignExtend(status_to_32(c_MCSR(procID).&mstatus))
        case 0x302, _       => c_MCSR(procID).&medeleg
        case 0x303, _       => c_MCSR(procID).&mideleg
        case 0x304, false   => c_MCSR(procID).&mie
        case 0x304, true    => SignExtend(ie_to_32(c_MCSR(procID).&mie))
        case 0x305, _       => c_MCSR(procID).mtvec

        -- machine trap handling
        case 0x340, _       => c_MCSR(procID).mscratch
        case 0x341, _       => c_MCSR(procID).mepc
        case 0x342, false   => c_MCSR(procID).&mcause
        case 0x342, true    => SignExtend(cause_to_32(c_MCSR(procID).&mcause))
        case 0x343, _       => c_MCSR(procID).mbadaddr
        case 0x344, false   => c_MCSR(procID).&mip
        case 0x344, true    => SignExtend(ip_to_32(c_MCSR(procID).&mip))

        -- machine protection and translation
        case 0x3A0, _       => c_MCSR(procID).pmpcfg0
        case 0x3A1, _       => c_MCSR(procID).pmpcfg1
        case 0x3A2, _       => c_MCSR(procID).pmpcfg2
        case 0x3A3, _       => c_MCSR(procID).pmpcfg3
        case 0x3B0, _       => c_MCSR(procID).pmpaddr0
        case 0x3B1, _       => c_MCSR(procID).pmpaddr1
        case 0x3B2, _       => c_MCSR(procID).pmpaddr2
        case 0x3B3, _       => c_MCSR(procID).pmpaddr3
        case 0x3B4, _       => c_MCSR(procID).pmpaddr4
        case 0x3B5, _       => c_MCSR(procID).pmpaddr5
        case 0x3B6, _       => c_MCSR(procID).pmpaddr6
        case 0x3B7, _       => c_MCSR(procID).pmpaddr7
        case 0x3B8, _       => c_MCSR(procID).pmpaddr8
        case 0x3B9, _       => c_MCSR(procID).pmpaddr9
        case 0x3BA, _       => c_MCSR(procID).pmpaddrA
        case 0x3BB, _       => c_MCSR(procID).pmpaddrB
        case 0x3BC, _       => c_MCSR(procID).pmpaddrC
        case 0x3BD, _       => c_MCSR(procID).pmpaddrD
        case 0x3BE, _       => c_MCSR(procID).pmpaddrE
        case 0x3BF, _       => c_MCSR(procID).pmpaddrF

        -- machine counter/timers
        case 0xF00, false   => c_MCSR(procID).mcycle
        case 0xF00, true    => SignExtend(c_MCSR(procID).mcycle<31:0>)
        case 0xF01, false   => c_MCSR(procID).mtime
        case 0xF01, true    => SignExtend(c_MCSR(procID).mtime<31:0>)
        case 0xF02, false   => c_MCSR(procID).minstret
        case 0xF02, true    => SignExtend(c_MCSR(procID).minstret<31:0>)
        case 0xF80, true    => SignExtend(c_MCSR(procID).mcycle<63:32>)
        case 0xF81, true    => SignExtend(c_MCSR(procID).mtime<63:32>)
        case 0xF82, true    => SignExtend(c_MCSR(procID).minstret<63:32>)

        -- machine counter-enables
        case 0x310, _       => c_MCSR(procID).&mucounteren
        case 0x311, _       => c_MCSR(procID).&mscounteren
        case 0x312, _       => c_MCSR(procID).&mhcounteren

        -- machine counter-deltas
        case 0x700, false   => c_MCSR(procID).mucycle_delta
        case 0x700, true    => SignExtend(c_MCSR(procID).mucycle_delta<31:0>)
        case 0x701, false   => c_MCSR(procID).mutime_delta
        case 0x701, true    => SignExtend(c_MCSR(procID).mutime_delta<31:0>)
        case 0x702, false   => c_MCSR(procID).muinstret_delta
        case 0x702, true    => SignExtend(c_MCSR(procID).muinstret_delta<31:0>)

        case 0x704, false   => c_MCSR(procID).mscycle_delta
        case 0x704, true    => SignExtend(c_MCSR(procID).mscycle_delta<31:0>)
        case 0x705, false   => c_MCSR(procID).mstime_delta
        case 0x705, true    => SignExtend(c_MCSR(procID).mstime_delta<31:0>)
        case 0x706, false   => c_MCSR(procID).msinstret_delta
        case 0x706, true    => SignExtend(c_MCSR(procID).msinstret_delta<31:0>)

        case 0x780, true    => SignExtend(c_MCSR(procID).mucycle_delta<63:32>)
        case 0x781, true    => SignExtend(c_MCSR(procID).mutime_delta<63:32>)
        case 0x782, true    => SignExtend(c_MCSR(procID).muinstret_delta<63:32>)

        case 0x784, true    => SignExtend(c_MCSR(procID).mscycle_delta<63:32>)
        case 0x785, true    => SignExtend(c_MCSR(procID).mstime_delta<63:32>)
        case 0x786, true    => SignExtend(c_MCSR(procID).msinstret_delta<63:32>)

        case _              => #UNDEFINED("unexpected CSR read at " : [csr])
      }

  assign value =
      match csr, in32BitMode()
      { -- user trap setup
        case 0x000, false   => c_MCSR(procID).mstatus   <- of_ustatus(ustatus(value), c_MCSR(procID).mstatus)
        case 0x000, true    => c_MCSR(procID).mstatus   <- of_ustatus(ustatus(status_of_32(value<31:0>)), c_MCSR(procID).mstatus)
        case 0x004, false   => c_MCSR(procID).mie       <- of_uie(uie(value), c_MCSR(procID).mie)
        case 0x004, true    => c_MCSR(procID).mie       <- of_uie(uie(ie_of_32(value<31:0>)), c_MCSR(procID).mie)
        case 0x005, _       => c_UCSR(procID).utvec     <- value

        -- user trap handling
        case 0x040, _       => c_UCSR(procID).uscratch  <- value
        case 0x041, _       => c_UCSR(procID).uepc      <- (value && SignExtend(0b100`3)) -- no 16-bit instr support
        case 0x042, false   => c_UCSR(procID).&ucause   <- value
        case 0x042, true    => c_UCSR(procID).&ucause   <- cause_of_32(value<31:0>)
        case 0x043, _       => c_UCSR(procID).ubadaddr  <- value
        case 0x044, false   => c_MCSR(procID).mip       <- of_uip(uip(value), c_MCSR(procID).mip)
        case 0x044, true    => c_MCSR(procID).mip       <- of_uip(uip(ip_of_32(value<31:0>)), c_MCSR(procID).mip)

        -- user floating-point context
        case 0x001, _       => { c_UCSR(procID).&fpcsr<4:0>     <- value<4:0>
                               ; c_MCSR(procID).mstatus.M_FS    <- ext_status(Dirty)
                               ; c_MCSR(procID).mstatus.M_SD    <- true
                               }
        case 0x002, _       => { c_UCSR(procID).fpcsr.FRM       <- value<2:0>
                               ; c_MCSR(procID).mstatus.M_FS    <- ext_status(Dirty)
                               ; c_MCSR(procID).mstatus.M_SD    <- true
                               }
        case 0x003, _       => { c_UCSR(procID).&fpcsr          <- value<31:0>
                               ; c_MCSR(procID).mstatus.M_FS    <- ext_status(Dirty)
                               ; c_MCSR(procID).mstatus.M_SD    <- true
                               }

        -- user counters/timers are URO

        -- supervisor trap setup
        case 0x100, false   => c_MCSR(procID).mstatus   <- of_sstatus(sstatus(value), c_MCSR(procID).mstatus)
        case 0x100, true    => c_MCSR(procID).mstatus   <- of_sstatus(sstatus(status_of_32(value<31:0>)), c_MCSR(procID).mstatus)
        case 0x102, _       => c_SCSR(procID).&sedeleg  <- value
        case 0x103, _       => c_SCSR(procID).&sideleg  <- value
        case 0x104, false   => c_MCSR(procID).mie       <- of_sie(sie(value), c_MCSR(procID).mie)
        case 0x104, true    => c_MCSR(procID).mie       <- of_sie(sie(ie_of_32(value<31:0>)), c_MCSR(procID).mie)
        case 0x105, _       => c_SCSR(procID).stvec     <- value

        -- supervisor trap handling
        case 0x140, _       => c_SCSR(procID).sscratch  <- value
        case 0x141, _       => c_SCSR(procID).sepc      <- (value && SignExtend(0b100`3)) -- no 16-bit instr support
        case 0x142, false   => c_SCSR(procID).&scause   <- value
        case 0x142, true    => c_SCSR(procID).&scause   <- cause_of_32(value<31:0>)
        case 0x143, _       => c_SCSR(procID).sbadaddr  <- value
        case 0x144, false   => c_MCSR(procID).mip       <- of_sip(sip(value), c_MCSR(procID).mip)
        case 0x144, true    => c_MCSR(procID).mip       <- of_sip(sip(ip_of_32(value<31:0>)), c_MCSR(procID).mip)

        -- supervisor protection and translation
        -- TODO: does this update flush the TLB cache?  does it flush the data cache?
        case 0x180, false   => c_SCSR(procID).sptbr     <- &sptbr64(value)
        case 0x180, true    => c_SCSR(procID).sptbr     <- SignExtend(&sptbr32(value<31:0>))

        -- supervisor counters/timers are SRO

        -- TODO: hypervisor register write support

        -- machine information registers are MRO

        -- machine trap setup
        --  these assignments are done with machine-level privilege;
        --  for now, we don't check for valid values.
        case 0x300, false   => c_MCSR(procID).&mstatus  <- value
        case 0x300, true    => c_MCSR(procID).&mstatus  <- status_of_32(value<31:0>)
        case 0x302, _       => c_MCSR(procID).&medeleg  <- value
        case 0x303, _       => c_MCSR(procID).&mideleg  <- value
        case 0x304, false   => c_MCSR(procID).&mie      <- value
        case 0x304, true    => c_MCSR(procID).&mie      <- ie_of_32(value<31:0>)
        case 0x305, _       => c_MCSR(procID).mtvec     <- value

        -- machine trap handling
        case 0x340, _       => c_MCSR(procID).mscratch  <- value
        case 0x341, _       => c_MCSR(procID).mepc      <- (value && SignExtend(0b100`3))  -- no 16-bit instr support
        case 0x342, false   => c_MCSR(procID).&mcause   <- value
        case 0x342, true    => c_MCSR(procID).&mcause   <- cause_of_32(value<31:0>)
        case 0x343, _       => c_MCSR(procID).mbadaddr  <- value
        case 0x344, false   => c_MCSR(procID).&mip      <- value
        case 0x344, true    => c_MCSR(procID).&mip      <- ip_of_32(value<31:0>)

        -- machine protection and translation
        case 0x3A0, _       => c_MCSR(procID).pmpcfg0      <- value
        case 0x3A1, _       => c_MCSR(procID).pmpcfg1      <- value
        case 0x3A2, _       => c_MCSR(procID).pmpcfg2      <- value
        case 0x3A3, _       => c_MCSR(procID).pmpcfg3      <- value
        case 0x3B0, _       => c_MCSR(procID).pmpaddr0     <- value
        case 0x3B1, _       => c_MCSR(procID).pmpaddr1     <- value
        case 0x3B2, _       => c_MCSR(procID).pmpaddr2     <- value
        case 0x3B3, _       => c_MCSR(procID).pmpaddr3     <- value
        case 0x3B4, _       => c_MCSR(procID).pmpaddr4     <- value
        case 0x3B5, _       => c_MCSR(procID).pmpaddr5     <- value
        case 0x3B6, _       => c_MCSR(procID).pmpaddr6     <- value
        case 0x3B7, _       => c_MCSR(procID).pmpaddr7     <- value
        case 0x3B8, _       => c_MCSR(procID).pmpaddr8     <- value
        case 0x3B9, _       => c_MCSR(procID).pmpaddr9     <- value
        case 0x3BA, _       => c_MCSR(procID).pmpaddrA     <- value
        case 0x3BB, _       => c_MCSR(procID).pmpaddrB     <- value
        case 0x3BC, _       => c_MCSR(procID).pmpaddrC     <- value
        case 0x3BD, _       => c_MCSR(procID).pmpaddrD     <- value
        case 0x3BE, _       => c_MCSR(procID).pmpaddrE     <- value
        case 0x3BF, _       => c_MCSR(procID).pmpaddrF     <- value

        -- machine counters/timers are MRO

        -- machine counter-enables
        case 0x310, _       => c_MCSR(procID).&mucounteren            <- value
        case 0x311, _       => c_MCSR(procID).&mscounteren            <- value
        case 0x312, _       => c_MCSR(procID).&mhcounteren            <- value

        -- machine counter-deltas
        case 0x700, _       => c_MCSR(procID).mucycle_delta           <- value
        case 0x701, _       => c_MCSR(procID).mutime_delta            <- value
        case 0x702, _       => c_MCSR(procID).muinstret_delta         <- value

        case 0x704, _       => c_MCSR(procID).mscycle_delta           <- value
        case 0x705, _       => c_MCSR(procID).mstime_delta            <- value
        case 0x706, _       => c_MCSR(procID).msinstret_delta         <- value

        case 0x780, true    => c_MCSR(procID).mucycle_delta<63:32>    <- value<31:0>
        case 0x781, true    => c_MCSR(procID).mutime_delta<63:32>     <- value<31:0>
        case 0x782, true    => c_MCSR(procID).muinstret_delta<63:32>  <- value<31:0>

        case 0x784, true    => c_MCSR(procID).mscycle_delta<63:32>    <- value<31:0>
        case 0x785, true    => c_MCSR(procID).mstime_delta<63:32>     <- value<31:0>
        case 0x786, true    => c_MCSR(procID).msinstret_delta<63:32>  <- value<31:0>

        case _, _           => #INTERNAL_ERROR("unexpected CSR write to " : [csr])
      }
}

string csrName(csr::creg) =
    match csr
    { -- user trap setup
      case 0x000  => "ustatus"
      case 0x004  => "uie"
      case 0x005  => "utvec"

      -- user floating-point context
      case 0x001  => "fflags"
      case 0x002  => "frm"
      case 0x003  => "fcsr"

      -- user counter/timers
      case 0xC00  => "cycle"
      case 0xC01  => "time"
      case 0xC02  => "instret"
      case 0xC80  => "cycleh"
      case 0xC81  => "timeh"
      case 0xC82  => "instreth"

      -- supervisor trap setup
      case 0x100  => "sstatus"
      case 0x102  => "sedeleg"
      case 0x103  => "sideleg"
      case 0x104  => "sie"
      case 0x105  => "stvec"

      -- supervisor trap handling
      case 0x140  => "sscratch"
      case 0x141  => "sepc"
      case 0x142  => "scause"
      case 0x143  => "sbadaddr"
      case 0x144  => "sip"

      -- supervisor protection and translation
      case 0x180  => "sptbr"

      -- supervisor counters/timers
      case 0xD00  => "scycle"
      case 0xD01  => "stime"
      case 0xD02  => "sinstret"
      case 0xD80  => "scycleh"
      case 0xD81  => "stimeh"
      case 0xD82  => "sinstreth"

      -- hypervisor trap setup
      case 0x200  => "hstatus"
      case 0x202  => "hedeleg"
      case 0x203  => "hideleg"
      case 0x204  => "hie"
      case 0x205  => "htvec"

      -- hypervisor trap handling
      case 0x240  => "hscratch"
      case 0x241  => "hepc"
      case 0x242  => "hcause"
      case 0x243  => "hbadaddr"

      -- hypervisor counters/timers
      case 0xE00  => "hcycle"
      case 0xE01  => "htime"
      case 0xE02  => "hinstret"
      case 0xE80  => "hcycleh"
      case 0xE81  => "htimeh"
      case 0xE82  => "hinstreth"

      -- machine information registers
      case 0xF10  => "misa"
      case 0xF11  => "mvendorid"
      case 0xF12  => "marchid"
      case 0xF13  => "mimpid"
      case 0xF14  => "mhartid"

      -- machine trap setup
      case 0x300  => "mstatus"
      case 0x302  => "medeleg"
      case 0x303  => "mideleg"
      case 0x304  => "mie"
      case 0x305  => "mtvec"

      -- machine trap handling
      case 0x340  => "mscratch"
      case 0x341  => "mepc"
      case 0x342  => "mcause"
      case 0x343  => "mbadaddr"
      case 0x344  => "mip"

      -- machine protection and translation
      case 0x3A0       => "pmpcfg0"
      case 0x3A1       => "pmpcfg1"
      case 0x3A2       => "pmpcfg2"
      case 0x3A3       => "pmpcfg3"
      case 0x3B0       => "pmpaddr0"
      case 0x3B1       => "pmpaddr1"
      case 0x3B2       => "pmpaddr2"
      case 0x3B3       => "pmpaddr3"
      case 0x3B4       => "pmpaddr4"
      case 0x3B5       => "pmpaddr5"
      case 0x3B6       => "pmpaddr6"
      case 0x3B7       => "pmpaddr7"
      case 0x3B8       => "pmpaddr8"
      case 0x3B9       => "pmpaddr9"
      case 0x3BA       => "pmpaddrA"
      case 0x3BB       => "pmpaddrB"
      case 0x3BC       => "pmpaddrC"
      case 0x3BD       => "pmpaddrD"
      case 0x3BE       => "pmpaddrE"
      case 0x3BF       => "pmpaddrF"

      -- machine counters/timers
      case 0xF00  => "mcycle"
      case 0xF01  => "mtime"
      case 0xF02  => "minstret"
      case 0xF80  => "mcycleh"
      case 0xF81  => "mtimeh"
      case 0xF82  => "minstreth"

      -- machine counter-enables
      case 0x310  => "mucounteren"
      case 0x311  => "mscounteren"
      case 0x312  => "mhcounteren"

      -- machine counter-deltas
      case 0x700  => "mucycle_delta"
      case 0x701  => "mutime_delta"
      case 0x702  => "muinstret_delta"

      case 0x704  => "mscycle_delta"
      case 0x705  => "mstime_delta"
      case 0x706  => "msinstret_delta"

      case 0x708  => "mhcycle_delta"
      case 0x709  => "mhtime_delta"
      case 0x70A  => "mhinstret_delta"

      case 0x780  => "mucycle_deltah"
      case 0x781  => "mutime_deltah"
      case 0x782  => "muinstret_deltah"

      case 0x784  => "mscycle_deltah"
      case 0x785  => "mstime_deltah"
      case 0x786  => "msinstret_deltah"

      case 0x788  => "mhcycle_deltah"
      case 0x789  => "mhtime_deltah"
      case 0x78A  => "mhinstret_deltah"

      case _      => "UNKNOWN"
    }

---------------------------------------------------------------------------
-- Tandem verification
---------------------------------------------------------------------------
-- This describes the state update due to every retired instruction,
-- which can be verified against an external oracle.  Currently, the
-- Cissr tool from Bluespec fills the role, and the record below is
-- designed against its API.

record StateDelta
{ exc_taken     :: bool                 -- whether an exception (interrupt/trap) was taken
  fetch_exc     :: bool                 -- whether that exception occured on fetch
                                --   if so, the retired instruction (rinstr) is undefined
  pc            :: regType              -- PC of retired instruction
  rinstr        :: word                 -- the retired instruction

  addr          :: regType option       -- address argument for instruction:
                                --   new control flow target for jump, exception branch, ERET
                                --   memory address for memory ops and AMOs
                                --   CSR register address for CSR instructions

  data1         :: regType option       -- data result for instruction:
                                --   new value for rd for ALU ops, LOAD, LOAD_FP, LR, SC, CSR ops
                                --   new csr_status for exceptions and ERET

  data2         :: regType option       -- data argument for instruction:
                                --   new csr_cause for exceptions
                                --   new memory value for STORE, STORE_FP, SC, AMOs
                                --   argument for CSR ops

  fp_data       :: fpval option         -- floating point value

  st_width      :: word option          -- width of store (optimization for sub-word store checks)
}

declare c_update :: id -> StateDelta

component Delta :: StateDelta
{ value        = c_update(procID)
  assign value = c_update(procID) <- value
}

unit setupDelta(pc::regType, instr::word) =
{ Delta.exc_taken <- false
; Delta.fetch_exc <- false
; Delta.pc        <- pc
; Delta.rinstr    <- instr
; Delta.addr      <- None
; Delta.data1     <- None
; Delta.data2     <- None
; Delta.fp_data   <- None
; Delta.st_width  <- None
}

unit recordLoad(addr::vAddr, val::regType) =
{ Delta.addr      <- Some(addr)
; Delta.data1     <- Some(val)
}

unit recordStore(addr::vAddr, val::regType, width::word) =
{ Delta.addr      <- Some(addr)
; Delta.data2     <- Some(val)
; Delta.st_width  <- Some(width)
}

unit recordException() =
{ Delta.exc_taken <- true }

unit recordFetchException(pc::regType) =
{ Delta.fetch_exc <- true
; Delta.pc        <- pc
}

---------------------------------------------------------------------------
-- Logging
---------------------------------------------------------------------------
string hex32(x::word)  = PadLeft(#"0", 8, [x])
string hex64(x::dword) = PadLeft(#"0", 16, [x])

string log_w_csr(csr::creg, data::regType) =
    "CSR (" : csrName(csr) : ") <- 0x" : hex64(data)

string reg(r::reg) =
{ if      r ==  0 then "$0"
  else if r ==  1 then "ra"
  else if r ==  2 then "sp"
  else if r ==  3 then "gp"
  else if r ==  4 then "tp"
  else if r ==  5 then "t0"
  else if r ==  6 then "t1"
  else if r ==  7 then "t2"
  else if r ==  8 then "fp"
  else if r ==  9 then "s1"
  else if r == 10 then "a0"
  else if r == 11 then "a1"
  else if r == 12 then "a2"
  else if r == 13 then "a3"
  else if r == 14 then "a4"
  else if r == 15 then "a5"
  else if r == 16 then "a6"
  else if r == 17 then "a7"
  else if r == 18 then "s2"
  else if r == 19 then "s3"
  else if r == 20 then "s4"
  else if r == 21 then "s5"
  else if r == 22 then "s6"
  else if r == 23 then "s7"
  else if r == 24 then "s8"
  else if r == 25 then "s9"
  else if r == 26 then "s10"
  else if r == 27 then "s11"
  else if r == 28 then "t3"
  else if r == 29 then "t4"
  else if r == 30 then "t5"
  else                 "t6"
}

string fpreg(r::reg) =
{ if      r ==  0 then "fs0"
  else if r ==  1 then "fs1"
  else if r ==  2 then "fs2"
  else if r ==  3 then "fs3"
  else if r ==  4 then "fs4"
  else if r ==  5 then "fs5"
  else if r ==  6 then "fs6"
  else if r ==  7 then "fs7"
  else if r ==  8 then "fs8"
  else if r ==  9 then "fs9"
  else if r == 10 then "fs10"
  else if r == 11 then "fs11"
  else if r == 12 then "fs12"
  else if r == 13 then "fs13"
  else if r == 14 then "fs14"
  else if r == 15 then "fs15"
  else if r == 16 then "fv0"
  else if r == 17 then "fv1"
  else if r == 18 then "fa0"
  else if r == 19 then "fa1"
  else if r == 20 then "fa2"
  else if r == 21 then "fa3"
  else if r == 22 then "fa4"
  else if r == 23 then "fa5"
  else if r == 24 then "fa6"
  else if r == 25 then "fa7"
  else if r == 26 then "ft0"
  else if r == 27 then "ft1"
  else if r == 28 then "ft2"
  else if r == 29 then "ft3"
  else if r == 30 then "ft4"
  else                 "ft5"
}

string log_w_gpr(r::reg, data::regType) =
    "Reg " : reg(r) : " (" : [[r]::nat] : ") <- 0x" : hex64(data)

string log_w_fprs(r::reg, data::word) =
    "FPR " : reg(r) : " (" : [[r]::nat] : ") <- 0x" : hex32(data)

string log_w_fprd(r::reg, data::regType) =
    "FPR " : reg(r) : " (" : [[r]::nat] : ") <- 0x" : hex64(data)

string log_w_mem_mask(pAddrIdx::pAddrIdx, vAddr::vAddr, mask::regType,
                      data::regType, old::regType, new::regType) =
    "MEM[0x" : hex64([pAddrIdx]) : "/" : hex64(vAddr) :
    "] <- (data: 0x" : hex64(data) : ", mask: 0x" : hex64(mask) :
    ", old: 0x"  : hex64(old) : ", new: 0x"  : hex64(new) : ")"

string log_w_mem_mask_misaligned(pAddrIdx::pAddrIdx, vAddr::vAddr, mask::regType,
                                 data::regType, align::nat, old::regType, new::regType) =
    "MEM[0x" : hex64([pAddrIdx]) : "/" : hex64(vAddr) : "/ misaligned@" : [align] :
    "] <- (data: 0x" : hex64(data) : ", mask: 0x" : hex64(mask) :
    ", old: 0x"  : hex64(old) : ", new: 0x"  : hex64(new) : ")"

string log_w_mem(pAddrIdx::pAddrIdx, vAddr::vAddr, data::regType) =
    "MEM[0x" : hex64([pAddrIdx]) : "/" : hex64(vAddr) :
    "] <- (data: 0x" : hex64(data) : ")"

string log_r_mem(pAddrIdx::pAddrIdx, vAddr::vAddr, data::regType) =
    "data <- MEM[0x" : PadLeft(#"0", 10, [pAddrIdx]) : "/" : hex64(vAddr) :
    "]: 0x" : hex64(data)

string log_exc(e::ExceptionType) =
    " Exception " : excName(e) : " raised!"

string log_tohost(tohost::regType) =
    "-> host: " : hex64(tohost)

nat LOG_IO      = 0
nat LOG_INSN    = 1
nat LOG_REG     = 2
nat LOG_MEM     = 3
nat LOG_ADDRTR  = 4

declare log :: (nat * string) list

unit mark_log(lvl::nat, s::string)  = log <- (lvl, s) @ log
unit clear_logs()                   = log <- Nil

---------------------------------------------------------------------------
-- Exception and Interrupt processing
---------------------------------------------------------------------------

-- Signalled exceptions are recorded as traps.

unit setTrap(e::ExceptionType, badaddr::vAddr option) =
{ var trap
; trap.trap             <- e
; trap.badaddr          <- badaddr
; NextFetch             <- Some(Trap(trap))
}

unit signalException(e::ExceptionType) =
{ mark_log(LOG_INSN, "signalling exception " : excName(e))
; setTrap(e, None)
; recordException()
}

unit signalAddressException(e::ExceptionType, vAddr::vAddr) =
{ mark_log(LOG_INSN, "signalling address exception " : excName(e) : " at " : [vAddr])
; setTrap(e, Some(vAddr))
; recordException()
}

unit signalEnvCall() =
  signalException(E_Env_Call)


-- Delegation logic.

Privilege excHandlerDelegate(delegate::Privilege, ec_idx::nat) =
{ match delegate
  { case Machine    => if MCSR.&medeleg<ec_idx>
                       then excHandlerDelegate(Hypervisor, ec_idx)
                       else Machine
    case Hypervisor => if HCSR.hedeleg<ec_idx>
                       then excHandlerDelegate(Supervisor, ec_idx)
                       else Hypervisor
    case Supervisor => if SCSR.&sedeleg<ec_idx>
                       then User
                       else Supervisor
    case User       => #INTERNAL_ERROR("Exception delegation failure")
  }
}

Privilege intHandlerDelegate(delegate::Privilege, int_idx::nat) =
{ match delegate
  { case Machine    => if MCSR.&mideleg<int_idx>
                       then intHandlerDelegate(Hypervisor, int_idx)
                       else Machine
    case Hypervisor => if HCSR.hideleg<int_idx>
                       then intHandlerDelegate(Supervisor, int_idx)
                       else Hypervisor
    case Supervisor => if SCSR.&sideleg<int_idx>
                       then User
                       else Supervisor
    case User       => #INTERNAL_ERROR("Interrupt delegation failure")
  }
}

-- Handling logic.

unit excHandler(intr::bool, ec::exc_code, fromPriv::Privilege, toPriv::Privilege,
                epc::regType, badaddr::vAddr option) =
{ mark_log(LOG_INSN, ["trapping from " : privName(fromPriv) : " to " : privName(toPriv) :
                      " at pc " : [epc] : (if intr then " intr:" else " exc:") : [[ec]::nat] :
                      [if IsSome(badaddr) then [" baddaddr:" : [ValOf(badaddr)]] else ""]])
; match toPriv
  { case Machine    => { MCSR.mstatus           <- menter(MCSR.mstatus, fromPriv)
                       ; MCSR.mepc              <- epc
                       ; MCSR.mcause.M_Intr     <- intr
                       ; MCSR.mcause.M_ExcCause <- ZeroExtend(ec)
                       ; MCSR.mbadaddr          <- if IsSome(badaddr) then ValOf(badaddr) else SignExtend(0b1`1)
                       ; PC                     <- MCSR.mtvec
                       }
    case Hypervisor => { MCSR.mstatus           <- henter(MCSR.mstatus, fromPriv)
                       ; HCSR.hepc              <- epc
                       ; HCSR.hcause.M_Intr     <- intr
                       ; HCSR.hcause.M_ExcCause <- ZeroExtend(ec)
                       ; PC                     <- HCSR.htvec
                       }
    case Supervisor => { MCSR.mstatus           <- senter(MCSR.mstatus, fromPriv)
                       ; SCSR.sepc              <- epc
                       ; SCSR.scause.M_Intr     <- intr
                       ; SCSR.scause.M_ExcCause <- ZeroExtend(ec)
                       ; PC                     <- SCSR.stvec
                       }
    case User       => { MCSR.mstatus           <- uenter(MCSR.mstatus, fromPriv)
                       ; UCSR.uepc              <- epc
                       ; UCSR.ucause.M_Intr     <- intr
                       ; UCSR.ucause.M_ExcCause <- ZeroExtend(ec)
                       ; PC                     <- UCSR.utvec
                       }
  }
; curPrivilege <- toPriv
}

-- Interrupts are globally enabled if the current privilege level is
-- lower than the interrupt delegatee, or if they are the same and
-- interrupts are enabled for that privilege in mstatus.
bool globallyEnabled(delegate::Privilege, cur::Privilege) =
{ match delegate, cur
  { case Machine,    Machine    => MCSR.mstatus.M_MIE
    case Machine,    _          => true

    case Hypervisor, Machine    => false
    case Hypervisor, Hypervisor => MCSR.mstatus.M_HIE
    case Hypervisor, _          => true

    case Supervisor, Supervisor => MCSR.mstatus.M_SIE
    case Supervisor, User       => true
    case Supervisor, _          => false

    case User,       User       => MCSR.mstatus.M_UIE
    case User,       _          => false
  }
}

-- Interrupts are prioritized in privilege order, and for each
-- privilege, in the order: external, software, timers.

-- The specification would be nicer if the interrupt indices preserved
-- the priority order, avoiding the need for this inefficient function.
(InterruptType * Privilege) option nextInterrupt(i::InterruptType) =
{ match i
  { case I_M_External => Some(I_M_Software, Machine)
    case I_M_Software => Some(I_M_Timer,    Machine)
    case I_M_Timer    => Some(I_H_External, Hypervisor)

    case I_H_External => Some(I_H_Software, Hypervisor)
    case I_H_Software => Some(I_H_Timer,    Hypervisor)
    case I_H_Timer    => Some(I_S_External, Supervisor)

    case I_S_External => Some(I_S_Software, Supervisor)
    case I_S_Software => Some(I_S_Timer,    Supervisor)
    case I_S_Timer    => Some(I_U_External, User)

    case I_U_External => Some(I_U_Software, User)
    case I_U_Software => Some(I_U_Timer,    User)
    case I_U_Timer    => None
  }
}

(InterruptType * Privilege) option searchDispatchableIntr(i::InterruptType, p::Privilege) =
{ int_idx = [interruptIndex(i)]::nat
; -- An interrupt is locally enabled if the interrupt is pending and
  -- enabled.
  locallyEnabled = MCSR.&mie<int_idx> and MCSR.&mip<int_idx>
; delegate = intHandlerDelegate(p, int_idx)
; if globallyEnabled(delegate, curPrivilege) and locallyEnabled
  then Some(i, delegate)
  else { match nextInterrupt(i)
         { case Some(ni, np) => searchDispatchableIntr(ni, np)
           case None         => None
         }
       }
}

(InterruptType * Privilege) option curInterrupt() =
{ m_enabled = (curPrivilege != Machine) or MCSR.mstatus.M_MIE
; if MCSR.&mip == 0 or not m_enabled then None -- fast path
  else searchDispatchableIntr(I_M_External, Machine)
}

---------------------------------------------------------------------------
-- CSR access with logging
---------------------------------------------------------------------------

component CSR(n::creg) :: regType
{ value        = CSRMap(n)
  assign value =  { CSRMap(n) <- value
                  ; mark_log(LOG_REG, log_w_csr(n, value))
                  }
}

unit writeCSR(csr::creg, val::regType) =
{ CSR(csr)      <- val;
  Delta.addr    <- Some(ZeroExtend(csr));
  Delta.data2   <- Some(CSR(csr))   -- Note that writes to CSR are intercepted
                                    -- and controlled by CSRMap, so we need to
                                    -- use what was finally written to the
                                    -- CSR, and not val itself.
}

---------------------------------------------------------------------------
-- GPR/FPR access with logging
---------------------------------------------------------------------------

component GPR(n::reg) :: regType
{ value        = if n == 0 then 0 else gpr(n)
  assign value = when n <> 0
                 do { gpr(n) <- value
                    ; mark_log(LOG_REG, log_w_gpr(n, value))
                    }
}

unit writeRD(rd::reg, val::regType) =
{ GPR(rd)       <- val
; Delta.data1   <- Some(val)
}

component FPRS(n::reg) :: word
{ value        = fpr(n)<31:0>
  assign value = { fpr(n)<31:0> <- value
                 ; mark_log(LOG_REG, log_w_fprs(n, value))
                 }
}

component FPRD(n::reg) :: regType
{ value        = fpr(n)
  assign value = { fpr(n) <- value
                 ; mark_log(LOG_REG, log_w_fprd(n, value))
                 }
}

unit writeFPRS(rd::reg, val::word) =
{ FPRS(rd)          <- val
; MCSR.mstatus.M_FS <- ext_status(Dirty)
; MCSR.mstatus.M_SD <- true
; Delta.data1       <- Some(ZeroExtend(val))
}

unit writeFPRD(rd::reg, val::regType) =
{ FPRD(rd)          <- val
; MCSR.mstatus.M_FS <- ext_status(Dirty)
; MCSR.mstatus.M_SD <- true
; Delta.data1       <- Some(val)
}

---------------------------------------------------------------------------
-- Raw memory access
---------------------------------------------------------------------------

declare MEM :: pAddrIdx -> regType -- raw memory, laid out in blocks
                                   -- of (|pAddr|-|pAddrIdx|) bits

-- Spike HTIF compatibility
-- The riscv-test suite uses the tohost MMIO port to indicate test completion
-- and pass/fail status.
declare htif_tohost_addr :: pAddr  -- address of tohost port
declare done :: bool               -- internal flag to request termination

unit initMem(val::regType) =
    MEM <- InitMap(val)

regType rawReadData(pAddr::pAddr) =
{ pAddrIdx = pAddr<63:3>
; align    = [pAddr<2:0>]::nat
; if align == 0   -- aligned read
  then { data = MEM(pAddrIdx)
       ; mark_log(LOG_MEM, log_r_mem(pAddrIdx,   pAddr, data))
       ; data
       }
  else { dw0   = MEM(pAddrIdx)
       ; dw1   = MEM(pAddrIdx+1)
       ; ddw   = (dw1 : dw0) >> (align * 8)
       ; data  = ddw<63:0>
       ; mark_log(LOG_MEM, log_r_mem(pAddrIdx,   pAddr, dw0))
       ; mark_log(LOG_MEM, log_r_mem(pAddrIdx+1, pAddr, dw1))
       ; mark_log(LOG_MEM, log_r_mem(pAddrIdx,   pAddr, data))
       ; data
       }
}

unit rawWriteData(pAddr::pAddr, data::regType, nbytes::nat) =
{ mask     = ([ZeroExtend(1`1)::regType] << (nbytes * 8)) - 1
; pAddrIdx = pAddr<63:3>
; align    = [pAddr<2:0>] :: nat
; old      = MEM(pAddrIdx)

; mark_log(LOG_MEM, log_r_mem(pAddrIdx, pAddr, old))

; if align == 0     -- aligned write
  then { new = old && ~mask || data && mask
       ; MEM(pAddrIdx) <- new
       ; mark_log(LOG_MEM, log_w_mem_mask(pAddrIdx, pAddr, mask, data, old, new))
       }
  else { if align + nbytes <= Size(mask) div 8      -- write to a single regType-sized block
         then { new = old && ~(mask << (align * 8)) || (data && mask) << (align * 8)
              ; MEM(pAddrIdx) <- new
              ; mark_log(LOG_MEM, log_w_mem_mask_misaligned(pAddrIdx, pAddr, mask, data, align, old, new))
              }
         -- write touching adjacent regType-sized blocks
         else { dw_old  = MEM(pAddrIdx+1) : old
              ; dw_data = ZeroExtend(data) << (align*8)
              ; dw_mask = ZeroExtend(mask) << (align*8)
              ; dw_new  = dw_old && ~dw_mask || dw_data && dw_mask
              ; MEM(pAddrIdx+1) <- dw_new<2*Size(data)-1:Size(data)>
              ; MEM(pAddrIdx)   <- dw_new<Size(data)-1:0>
              }
       }
; if pAddr == htif_tohost_addr
  then { mark_log(LOG_MEM, log_tohost(data))
       ; ExitCode <- data
       ; done     <- true
       }
  else ()
}

word rawReadInst(pAddr::pAddr) =
{ pAddrIdx = pAddr<63:3>
; data     = MEM(pAddrIdx)
; mark_log(LOG_MEM, log_r_mem(pAddrIdx, pAddr, data))
; if pAddr<2> then data<63:32> else data<31:0>
}

-- helper used to preload memory contents
unit rawWriteMem(pAddr::pAddr, data::regType) =
{ pAddrIdx = pAddr<63:3>
; MEM(pAddrIdx) <- data
; mark_log(LOG_MEM, log_w_mem(pAddrIdx, pAddr, data))
}

---------------------------------------------------------------------------
-- Address Translation
---------------------------------------------------------------------------

nat PAGESIZE_BITS     = 12

-- internal defines for TLB implementation
nat  TLBEntries       = 16
type tlbIdx           = bits(4)

-- memory permissions

type permType = bits(4)

register memPerm :: permType
{ 3 : Mem_U
, 2 : Mem_X
, 1 : Mem_W
, 0 : Mem_R
}

bool checkMemPermission(ac::accessType, priv::Privilege, mxr::bool, pum::bool, p::memPerm) =
{ match ac, priv
  { case Read,      User        => (p.Mem_R or (mxr and p.Mem_X)) and p.Mem_U
    case Write,     User        => p.Mem_W and p.Mem_U
    case ReadWrite, User        => (p.Mem_R or (mxr and p.Mem_X)) and p.Mem_W and p.Mem_U
    case Execute,   User        => p.Mem_X and p.Mem_U
    case Read,      Supervisor  => (p.Mem_R or (mxr and p.Mem_X)) and !(p.Mem_U and pum)
    case Write,     Supervisor  => p.Mem_W and !(p.Mem_U and pum)
    case ReadWrite, Supervisor  => (p.Mem_R or (mxr and p.Mem_X)) and p.Mem_W and !(p.Mem_U and pum)
    case Execute,   Supervisor  => p.Mem_X and !(p.Mem_U and pum)
    case _,         Hypervisor  => #INTERNAL_ERROR("hypervisor 32-bit mem perm check") -- should not happen
    case _,         Machine     => #INTERNAL_ERROR("machine 32-bit mem perm check")    -- should not happen
  }
}

bool isPTEPtr(perm::permType) = perm<2:0> == 0

-- Sv32 memory translation
--------------------------

nat VPN32_LEVEL_BITS  = 10
nat PPN32_LEVEL_BITS  = 10
nat PTE32_LOG_SIZE    =  2
nat SV32_LEVELS       =  2

type vaddr32  = bits(32)
type paddr32  = bits(34)
type pte32    = bits(32)

register SV32_Vaddr :: vaddr32
{ 31-12 : VA32_VPNi    -- VPN[1,0]
, 11-0  : VA32_PgOfs   -- page offset
}

register SV32_Paddr :: paddr32
{ 33-12 : PA32_PPNi    -- PPN[1,0]
, 11-0  : PA32_PgOfs   -- page offset
}

register SV32_PTE   :: pte32
{ 31-10 : PTE32_PPNi   -- PPN[1,0]
,     7 : PTE32_D      -- dirty
,     6 : PTE32_A      -- accessed
,     5 : PTE32_G      -- global
,   4-1 : PTE32_PERM   -- permissions
,     0 : PTE32_V      -- valid
}

paddr32 curPTB32() =
    (ZeroExtend(sptbr32(SCSR.sptbr<31:0>).PPN_32) << PAGESIZE_BITS)

-- 32-bit page table walker.  This returns the physical address for
-- the input vaddr32 as the first element of the returned tuple.  The
-- remaining elements are for the TLB implementation: the PTE entry
-- itself, the address of the PTE in memory (so that it can be
-- updated) by the TLB, the level of the PTE entry, and whether the
-- mapping is marked as a global mapping.

(paddr32 * SV32_PTE * paddr32 * nat * bool) option
walk32(vaddr::vaddr32, ac::accessType, priv::Privilege, mxr::bool, pum::bool,
       ptb::paddr32, level::nat, global::bool) =
{ va        = SV32_Vaddr(vaddr)
; pt_ofs    = ZeroExtend((va.VA32_VPNi >>+ (level * VPN32_LEVEL_BITS))<(VPN32_LEVEL_BITS-1):0>) << PTE32_LOG_SIZE
; pte_addr  = ptb + pt_ofs
; pte       = SV32_PTE(rawReadData(ZeroExtend(pte_addr))<31:0>)
; mperm     = memPerm(pte.PTE32_PERM)
; mark_log(LOG_ADDRTR, ["walk32(vaddr=0x" : PadLeft(#"0", 16, [&va]) : "): level=" : [level]
                        : " pt_base=0x" : PadLeft(#"0", 16, [ptb])
                        : " pt_ofs=" : [[pt_ofs]::nat]
                        : " pte_addr=0x" : PadLeft(#"0", 16, [pte_addr])
                        : " pte=0x" : PadLeft(#"0", 16, [&pte])])
; if (not pte.PTE32_V) or (mperm.Mem_W and not mperm.Mem_R)
  then { mark_log(LOG_ADDRTR, "walk32: invalid PTE")
       ; None
       }
  else { if not (mperm.Mem_R or mperm.Mem_X)
         then { -- ptr to next level
                if level == 0
                then { mark_log(LOG_ADDRTR, "last-level PTE contains a pointer!")
                     ; None
                     }
                else walk32(vaddr, ac, priv, mxr, pum,
                            ZeroExtend(pte.PTE32_PPNi << PAGESIZE_BITS), level - 1, global or pte.PTE32_G)
              }
         else { -- leaf PTE
                if not checkMemPermission(ac, priv, mxr, pum, mperm)
                then { mark_log(LOG_ADDRTR, "PTE permission check failure!")
                     ; None
                     }
                else { -- compute translated address
                       ppn = if level > 0
                             then ((ZeroExtend((pte.PTE32_PPNi >>+ (level * PPN32_LEVEL_BITS))
                                               << (level * PPN32_LEVEL_BITS)))
                                   || ZeroExtend(va.VA32_VPNi && ((1 << (level * VPN32_LEVEL_BITS)) - 1)))
                             else pte.PTE32_PPNi
                     ; Some(ZeroExtend(ppn : va.VA32_PgOfs), pte, pte_addr, level, global or pte.PTE32_G)
                     }
              }
       }
}

-- returns an updated PTE for an access, if needed
SV32_PTE option updatePTE32(pte::SV32_PTE, ac::accessType) =
{ d_update = (ac == Write or ac == ReadWrite) and (not pte.PTE32_D)
; a_update = not pte.PTE32_A
; if d_update or a_update
  then { var pte_w = pte
       ; pte_w.PTE32_A <- true
       ; when d_update do pte_w.PTE32_D <- true
       ; Some(pte_w)
       }
  else None
}

-- 32-bit TLB
---------------------------------------------------------------------------
-- The spec does not mention a TLB, but we would like to capture part
-- of the semantics of SFENCE.  The TLB also improves simulation
-- speed.

-- This implementation stores the global mapping bit from the PTE in
-- the TLB.  This causes an asymmetry between TLB lookup and TLB
-- flush, due to the spec's treatment of an ASID=0 in SFENCE.VM:
--
-- * in TLB lookup, the global bit is used to check for a global
--   match, and this global bit when set overrides the input ASID.
--
-- * in TLB flush, an input ASID of 0 overrides the global bit when
--   checking if a TLB entry needs to be flushed.

-- Each TLBEntry also stores the full PTE and its pAddr, so that it
-- can write back the PTE when its dirty bit needs to be updated.

record TLB32_Entry
{ asid_32       :: asid32
  global_32     :: bool
  vAddr_32      :: vaddr32      -- VPN
  vMatchMask_32 :: vaddr32      -- matching mask for superpages

  pAddr_32      :: paddr32      -- PPN
  vAddrMask_32  :: vaddr32      -- selection mask for superpages

  pte_32        :: SV32_PTE     -- for permissions and dirty bit writeback
  pteAddr_32    :: paddr32

  age_32        :: regType      -- derived from cycles
}

TLB32_Entry mkTLB32_Entry(asid::asid32, global::bool, vAddr::vaddr32, pAddr::paddr32,
                          pte::SV32_PTE, i::nat, pteAddr::paddr32) =
{ var ent :: TLB32_Entry
; ent.asid_32       <- asid
; ent.global_32     <- global
; ent.pte_32        <- pte
; ent.pteAddr_32    <- pteAddr
; ent.vAddrMask_32  <- ((1::vaddr32) << ((VPN32_LEVEL_BITS*i) + PAGESIZE_BITS)) - 1
; ent.vMatchMask_32 <- (SignExtend('1')::vaddr32) ?? ent.vAddrMask_32
; ent.vAddr_32      <- vAddr && ent.vMatchMask_32
; ent.pAddr_32      <- (pAddr >> (PAGESIZE_BITS + (PPN32_LEVEL_BITS*i))) << (PAGESIZE_BITS + (PPN32_LEVEL_BITS*i))
; ent.age_32        <- c_cycles(procID)
; ent
}

type TLB32_Map  = tlbIdx -> TLB32_Entry option

(TLB32_Entry * tlbIdx) option lookupTLB32(asid::asid32, vAddr::vaddr32, tlb::TLB32_Map) =
{ var ent = None
; for i in 0 .. TLBEntries - 1 do
  { match tlb([i])
    { case Some(e) => when ent == None and (e.global_32 or e.asid_32 == asid)
                           and (e.vAddr_32 == vAddr && e.vMatchMask_32)
                      do ent <- Some(e, [i])
      case None    => ()
    }
  }
; ent
}

TLB32_Map addToTLB32(asid::asid32, vAddr::vaddr32, pAddr::paddr32, pte::SV32_PTE, pteAddr::paddr32,
                     i::nat, global::bool, curTLB::TLB32_Map) =
{ var ent       = mkTLB32_Entry(asid, global, vAddr, pAddr, pte, i, pteAddr)
; var tlb       = curTLB
; var current   = SignExtend('1')
; var addIdx    = 0
; var added     = false
; for i in 0 .. TLBEntries - 1 do
  { match tlb([i])
    { case Some(e)  => when e.age_32 <+ current
                       do { current     <- e.age_32
                          ; addIdx      <- i
                          }
      case None     => { tlb([i])    <- Some(ent)
                       ; added       <- true
                       }
    }
  }
; when not added
  do tlb([addIdx]) <- Some(ent)
; tlb
}

TLB32_Map flushTLB32(asid::asid32, addr::vaddr32 option, curTLB::TLB32_Map) =
{ var tlb = curTLB
; for i in 0 .. TLBEntries - 1 do
  { match tlb([i]), addr
    { case Some(e), Some(va)    => when (asid == 0 or (asid == e.asid_32 and not e.global_32))
                                        and (e.vAddr_32 == va && e.vMatchMask_32)
                                   do tlb([i]) <- None
      case Some(e), None        => when asid == 0 or (asid == e.asid_32 and not e.global_32)
                                   do tlb([i]) <- None
      case None,    _           => ()
    }
  }
; tlb
}

declare  c_tlb32 :: id -> TLB32_Map

component TLB32 :: TLB32_Map
{ value        = c_tlb32(procID)
  assign value = c_tlb32(procID) <- value
}

-- Sv32 address translation

paddr32 option translate32(vAddr::vaddr32, ac::accessType, priv::Privilege, mxr::bool, pum::bool, level::nat) =
{ asid = curAsid32()
; match lookupTLB32(asid, vAddr, TLB32)
  { case Some(ent, idx) =>
    { if checkMemPermission(ac, priv, mxr, pum, memPerm(ent.pte_32.PTE32_PERM))
      then { mark_log(LOG_ADDRTR, "TLB32 hit!")
           -- update dirty bit in page table and TLB if needed
           ; pte_new = updatePTE32(ent.pte_32, ac)
           ; when IsSome(pte_new)
             do { pte = ValOf(pte_new)
                ; rawWriteData(ZeroExtend(ent.pteAddr_32), ZeroExtend(ent.&pte_32), 4)
                ; var tlb = TLB32
                ; tlb([idx]) <- Some(ent)
                ; TLB32 <- tlb
                }
           ; Some(ent.pAddr_32 || ZeroExtend(vAddr && ent.vAddrMask_32))
           }
      else { mark_log(LOG_ADDRTR, "TLB32 permission check failure")
           ; None
           }
    }
    case None =>
    { mark_log(LOG_ADDRTR, "TLB32 miss!")
    ; match walk32(vAddr, ac, priv, mxr, pum, curPTB32(), level, false)
      { case Some(pAddr, pte, pteAddr, i, global)  =>
        { TLB32 <- addToTLB32(asid, vAddr, pAddr, pte, pteAddr, i, global, TLB32)
        ; Some(pAddr)
        }
        case None   => None
      }
    }
  }
}

-- Sv39 memory translation
--------------------------

nat VPN39_LEVEL_BITS  = 9
nat PPN39_LEVEL_BITS  = 9
nat PTE39_LOG_SIZE    = 3
nat SV39_LEVELS       = 3

type vaddr39  = bits(39)
type paddr39  = bits(50)
type pte39    = dword

register SV39_Vaddr :: vaddr39
{ 38-12 : VA39_VPNi    -- VPN[1,0]
, 11-0  : VA39_PgOfs   -- page offset
}

register SV39_Paddr :: paddr39
{ 49-12 : PA39_PPNi    -- PPN[1,0]
, 11-0  : PA39_PgOfs   -- page offset
}

register SV39_PTE   :: pte39
{ 47-10 : PTE39_PPNi   -- PPN[1,0]
,     7 : PTE39_D      -- dirty
,     6 : PTE39_A      -- accessed
,     5 : PTE39_G      -- global
,   4-1 : PTE39_PERM   -- permissions
,     0 : PTE39_V      -- valid
}

paddr39 curPTB39() =
    (ZeroExtend(sptbr64(SCSR.sptbr).PPN_64) << PAGESIZE_BITS)

-- 64-bit page table walker.  This returns the physical address for
-- the input vaddr39 as the first element of the returned tuple.  The
-- remaining elements are for the TLB implementation: the PTE entry
-- itself, the address of the PTE in memory (so that it can be
-- updated) by the TLB, the level of the PTE entry, and whether the
-- mapping is marked as a global mapping.

(paddr39 * SV39_PTE * paddr39 * nat * bool) option
walk39(vaddr::vaddr39, ac::accessType, priv::Privilege, mxr::bool, pum::bool,
       ptb::paddr39, level::nat, global::bool) =
{ va        = SV39_Vaddr(vaddr)
; pt_ofs    = ZeroExtend((va.VA39_VPNi >>+ (level * VPN39_LEVEL_BITS))<(VPN39_LEVEL_BITS-1):0>) << PTE39_LOG_SIZE
; pte_addr  = ptb + pt_ofs
; pte       = SV39_PTE(rawReadData(ZeroExtend(pte_addr)))
; mperm     = memPerm(pte.PTE39_PERM)
; mark_log(LOG_ADDRTR, ["walk32(vaddr=0x" : PadLeft(#"0", 16, [&va]) : "): level=" : [level]
                        : " pt_base=0x" : PadLeft(#"0", 16, [ptb])
                        : " pt_ofs=" : [[pt_ofs]::nat]
                        : " pte_addr=0x" : PadLeft(#"0", 16, [pte_addr])
                        : " pte=0x" : PadLeft(#"0", 16, [&pte])])
; if (not pte.PTE39_V) or (mperm.Mem_W and not mperm.Mem_R)
  then { mark_log(LOG_ADDRTR, "walk39: invalid PTE")
       ; None
       }
  else { if not (mperm.Mem_R or mperm.Mem_X)
         then { -- ptr to next level
                if level == 0
                then { mark_log(LOG_ADDRTR, "last-level PTE contains a pointer!")
                     ; None
                     }
                else walk39(vaddr, ac, priv, mxr, pum,
                            ZeroExtend(pte.PTE39_PPNi << PAGESIZE_BITS), level - 1, global or pte.PTE39_G)
              }
         else { -- leaf PTE
                if not checkMemPermission(ac, priv, mxr, pum, mperm)
                then { mark_log(LOG_ADDRTR, "PTE permission check failure!")
                     ; None
                     }
                else { -- compute translated address
                       ppn = if level > 0
                             then ((ZeroExtend((pte.PTE39_PPNi >>+ (level * PPN39_LEVEL_BITS))
                                               << (level * PPN39_LEVEL_BITS)))
                                   || ZeroExtend(va.VA39_VPNi && ((1 << (level * VPN39_LEVEL_BITS)) - 1)))
                             else pte.PTE39_PPNi
                     ; Some(ZeroExtend(ppn : va.VA39_PgOfs), pte, pte_addr, level, global or pte.PTE39_G)
                     }
              }
       }
}

-- returns an updated PTE for an access, if needed
SV39_PTE option updatePTE39(pte::SV39_PTE, ac::accessType) =
{ d_update = (ac == Write or ac == ReadWrite) and (not pte.PTE39_D)
; a_update = not pte.PTE39_A
; if d_update or a_update
  then { var pte_w = pte
       ; pte_w.PTE39_A <- true
       ; when d_update do pte_w.PTE39_D <- true
       ; Some(pte_w)
       }
  else None
}

-- 64-bit TLB
---------------------------------------------------------------------------
-- The spec does not mention a TLB, but we would like to capture part
-- of the semantics of SFENCE.  The TLB also improves simulation
-- speed.

-- This implementation stores the global mapping bit from the PTE in
-- the TLB.  This causes an asymmetry between TLB lookup and TLB
-- flush, due to the spec's treatment of an ASID=0 in SFENCE.VM:
--
-- * in TLB lookup, the global bit is used to check for a global
--   match, and this global bit when set overrides the input ASID.
--
-- * in TLB flush, an input ASID of 0 overrides the global bit when
--   checking if a TLB entry needs to be flushed.

-- Each TLBEntry also stores the full PTE and its pAddr, so that it
-- can write back the PTE when its dirty bit needs to be updated.

record TLB39_Entry
{ asid_39       :: asid64
  global_39     :: bool
  vAddr_39      :: vaddr39      -- VPN
  vMatchMask_39 :: vaddr39      -- matching mask for superpages

  pAddr_39      :: paddr39      -- PPN
  vAddrMask_39  :: vaddr39      -- selection mask for superpages

  pte_39        :: SV39_PTE     -- for permissions and dirty bit writeback
  pteAddr_39    :: paddr39

  age_39        :: regType      -- derived from cycles
}

TLB39_Entry mkTLB39_Entry(asid::asid64, global::bool, vAddr::vaddr39, pAddr::paddr39,
                          pte::SV39_PTE, i::nat, pteAddr::paddr39) =
{ var ent :: TLB39_Entry
; ent.asid_39       <- asid
; ent.global_39     <- global
; ent.pte_39        <- pte
; ent.pteAddr_39    <- pteAddr
; ent.vAddrMask_39  <- ((1::vaddr39) << ((VPN39_LEVEL_BITS*i) + PAGESIZE_BITS)) - 1
; ent.vMatchMask_39 <- (SignExtend('1')::vaddr39) ?? ent.vAddrMask_39
; ent.vAddr_39      <- vAddr && ent.vMatchMask_39
; ent.pAddr_39      <- (pAddr >> (PAGESIZE_BITS + (PPN39_LEVEL_BITS*i))) << (PAGESIZE_BITS + (PPN39_LEVEL_BITS*i))
; ent.age_39        <- c_cycles(procID)
; ent
}

type TLB39_Map  = tlbIdx -> TLB39_Entry option

(TLB39_Entry * tlbIdx) option lookupTLB39(asid::asid64, vAddr::vaddr39, tlb::TLB39_Map) =
{ var ent = None
; for i in 0 .. TLBEntries - 1 do
  { match tlb([i])
    { case Some(e) => when ent == None and (e.global_39 or e.asid_39 == asid)
                           and (e.vAddr_39 == vAddr && e.vMatchMask_39)
                      do ent <- Some(e, [i])
      case None    => ()
    }
  }
; ent
}

TLB39_Map addToTLB39(asid::asid64, vAddr::vaddr39, pAddr::paddr39, pte::SV39_PTE, pteAddr::paddr39,
                     i::nat, global::bool, curTLB::TLB39_Map) =
{ var ent       = mkTLB39_Entry(asid, global, vAddr, pAddr, pte, i, pteAddr)
; var tlb       = curTLB
; var current   = SignExtend('1')
; var addIdx    = 0
; var added     = false
; for i in 0 .. TLBEntries - 1 do
  { match tlb([i])
    { case Some(e)  => when e.age_39 <+ current
                       do { current     <- e.age_39
                          ; addIdx      <- i
                          }
      case None     => { tlb([i])    <- Some(ent)
                       ; added       <- true
                       }
    }
  }
; when not added
  do tlb([addIdx]) <- Some(ent)
; tlb
}

TLB39_Map flushTLB39(asid::asid64, addr::vaddr39 option, curTLB::TLB39_Map) =
{ var tlb = curTLB
; for i in 0 .. TLBEntries - 1 do
  { match tlb([i]), addr
    { case Some(e), Some(va)    => when (asid == 0 or (asid == e.asid_39 and not e.global_39))
                                        and (e.vAddr_39 == va && e.vMatchMask_39)
                                   do tlb([i]) <- None
      case Some(e), None        => when asid == 0 or (asid == e.asid_39 and not e.global_39)
                                   do tlb([i]) <- None
      case None,    _           => ()
    }
  }
; tlb
}

declare  c_tlb39 :: id -> TLB39_Map

component TLB39 :: TLB39_Map
{ value        = c_tlb39(procID)
  assign value = c_tlb39(procID) <- value
}

-- Sv39 address translation

paddr39 option translate39(vAddr::vaddr39, ac::accessType, priv::Privilege, mxr::bool, pum::bool, level::nat) =
{ asid = curAsid64()
; match lookupTLB39(asid, vAddr, TLB39)
  { case Some(ent, idx) =>
    { if checkMemPermission(ac, priv, mxr, pum, memPerm(ent.pte_39.PTE39_PERM))
      then { mark_log(LOG_ADDRTR, "TLB39 hit!")
           -- update dirty bit in page table and TLB if needed
           ; pte_new = updatePTE39(ent.pte_39, ac)
           ; when IsSome(pte_new)
             do { pte = ValOf(pte_new)
                ; rawWriteData(ZeroExtend(ent.pteAddr_39), ZeroExtend(ent.&pte_39), 8)
                ; var tlb = TLB39
                ; tlb([idx]) <- Some(ent)
                ; TLB39 <- tlb
                }
           ; Some(ent.pAddr_39 || ZeroExtend(vAddr && ent.vAddrMask_39))
           }
      else { mark_log(LOG_ADDRTR, "TLB39 permission check failure")
           ; None
           }
    }
    case None =>
    { mark_log(LOG_ADDRTR, "TLB39 miss!")
    ; match walk39(vAddr, ac, priv, mxr, pum, curPTB39(), level, false)
      { case Some(pAddr, pte, pteAddr, i, global)  =>
        { TLB39 <- addToTLB39(asid, vAddr, pAddr, pte, pteAddr, i, global, TLB39)
        ; Some(pAddr)
        }
        case None   => None
      }
    }
  }
}

-- address translation dispatcher

pAddr option translateAddr(vAddr::regType, ac::accessType, ft::fetchType) =
{ priv = match ft
         { case Instruction => curPrivilege
           case Data        => if MCSR.mstatus.M_MPRV
                               then privilege(MCSR.mstatus.M_MPP)
                               else curPrivilege
         }
; mxr  = MCSR.mstatus.M_MXR
; pum  = MCSR.mstatus.M_PUM
; match vmType(MCSR.mstatus.M_VM), priv
  { case Mbare, _
    or       _,    Machine
    or       _, Hypervisor  => Some(vAddr)  -- no translation

    {- Comment out base/bound modes since there are no tests for them.

    case Mbb,   Machine
    or   Mbbid, Machine     => Some(vAddr)

     -}

    case Sv32,  _           => match translate32(vAddr<31:0>, ac, priv, mxr, pum, SV32_LEVELS)
                               { case Some(pa32)  => Some(ZeroExtend(pa32))
                                 case None        => None
                               }
    case Sv39,  _           => match translate39(vAddr<38:0>, ac, priv, mxr, pum, SV39_LEVELS)
                               { case Some(pa39)  => Some(ZeroExtend(pa39))
                                 case None        => None
                               }

--  case Sv48,  _           => translate64(vAddr, ft, ac, priv, 3)

    case     _,          _  => None
  }
}

---------------------------------------------------------------------------
-- Load Reservation
---------------------------------------------------------------------------

bool matchLoadReservation(vAddr::vAddr) =
    IsSome(ReserveLoad) and ValOf(ReserveLoad) == vAddr

---------------------------------------------------------------------------
-- Control Flow
---------------------------------------------------------------------------

unit branchTo(newPC::regType) =
{ NextFetch             <- Some(BranchTo(newPC))
; Delta.addr            <- Some(newPC)
}

unit noBranch(nextPC::regType) =
{ Delta.addr <- Some(nextPC) }

---------------------------------------------------------------------------
-- Integer Computational Instructions
---------------------------------------------------------------------------

-- Integer register-immediate

-----------------------------------
-- ADDI  rd, rs1, imm
-----------------------------------
define ArithI > ADDI(rd::reg, rs1::reg, imm::imm12) =
    writeRD(rd, GPR(rs1) + SignExtend(imm))

-----------------------------------
-- ADDIW rd, rs1, imm   (RV64I)
-----------------------------------
define ArithI > ADDIW(rd::reg, rs1::reg, imm::imm12) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else { temp = GPR(rs1) + SignExtend(imm)
         ; writeRD(rd, SignExtend(temp<31:0>))
         }

-----------------------------------
-- SLTI  rd, rs1, imm
-----------------------------------
define ArithI > SLTI(rd::reg, rs1::reg, imm::imm12) =
{ v1 = if in32BitMode() then SignExtend(GPR(rs1)<31:0>) else GPR(rs1)
; writeRD(rd, [v1 < SignExtend(imm)])
}

-----------------------------------
-- SLTIU rd, rs1, imm
-----------------------------------
define ArithI > SLTIU(rd::reg, rs1::reg, imm::imm12) =
{ v1 = if in32BitMode() then SignExtend(GPR(rs1)<31:0>) else GPR(rs1)
; writeRD(rd, [v1 <+ SignExtend(imm)])
}

-----------------------------------
-- ANDI  rd, rs1, imm
-----------------------------------
define ArithI > ANDI(rd::reg, rs1::reg, imm::imm12) =
    writeRD(rd, GPR(rs1) && SignExtend(imm))

-----------------------------------
-- ORI   rd, rs1, imm
-----------------------------------
define ArithI > ORI(rd::reg, rs1::reg, imm::imm12) =
    writeRD(rd, GPR(rs1) || SignExtend(imm))

-----------------------------------
-- XORI  rd, rs1, imm
-----------------------------------
define ArithI > XORI(rd::reg, rs1::reg, imm::imm12) =
    writeRD(rd, GPR(rs1) ?? SignExtend(imm))


-----------------------------------
-- SLLI  rd, rs1, imm
-----------------------------------
define Shift > SLLI(rd::reg, rs1::reg, imm::bits(6)) =
    if in32BitMode() and imm<5>
    then signalException(E_Illegal_Instr)
    else writeRD(rd, GPR(rs1) << [imm])

-----------------------------------
-- SRLI  rd, rs1, imm
-----------------------------------
define Shift > SRLI(rd::reg, rs1::reg, imm::bits(6)) =
    if in32BitMode() and imm<5>
    then signalException(E_Illegal_Instr)
    else { v1 = if in32BitMode() then ZeroExtend(GPR(rs1)<31:0>) else GPR(rs1)
         ; writeRD(rd, v1 >>+ [imm])
         }

-----------------------------------
-- SRAI  rd, rs1, imm
-----------------------------------
define Shift > SRAI(rd::reg, rs1::reg, imm::bits(6)) =
    if in32BitMode() and imm<5>
    then signalException(E_Illegal_Instr)
    else { v1 = if in32BitMode() then SignExtend(GPR(rs1)<31:0>) else GPR(rs1)
         ; writeRD(rd, v1 >> [imm])
         }

-----------------------------------
-- SLLIW rd, rs1, imm   (RV64I)
-----------------------------------
define Shift > SLLIW(rd::reg, rs1::reg, imm::bits(5)) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else writeRD(rd, SignExtend(GPR(rs1)<31:0> << [imm]))

-----------------------------------
-- SRLIW rd, rs1, imm   (RV64I)
-----------------------------------
define Shift > SRLIW(rd::reg, rs1::reg, imm::bits(5)) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else writeRD(rd, SignExtend(GPR(rs1)<31:0> >>+ [imm]))

-----------------------------------
-- SRAIW rd, rs1, imm   (RV64I)
-----------------------------------
define Shift > SRAIW(rd::reg, rs1::reg, imm::bits(5)) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else writeRD(rd, SignExtend(GPR(rs1)<31:0> >> [imm]))

-----------------------------------
-- LUI   rd, imm
-----------------------------------
define ArithI > LUI(rd::reg, imm::imm20) =
    writeRD(rd, SignExtend(imm : 0`12))

-----------------------------------
-- AUIPC rd, imm
-----------------------------------
define ArithI > AUIPC(rd::reg, imm::imm20) =
    writeRD(rd, PC + SignExtend(imm : 0`12))


-- Integer register-register

-----------------------------------
-- ADD   rd, rs1, rs2
-----------------------------------
define ArithR > ADD(rd::reg, rs1::reg, rs2::reg) =
    writeRD(rd, GPR(rs1) + GPR(rs2))

-----------------------------------
-- ADDW  rd, rs1, rs2   (RV64I)
-----------------------------------
define ArithR > ADDW(rd::reg, rs1::reg, rs2::reg) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else writeRD(rd, SignExtend(GPR(rs1)<31:0> + GPR(rs2)<31:0>))

-----------------------------------
-- SUB   rd, rs1, rs2
-----------------------------------
define ArithR > SUB(rd::reg, rs1::reg, rs2::reg) =
    writeRD(rd, GPR(rs1) - GPR(rs2))

-----------------------------------
-- SUBW  rd, rs1, rs2   (RV64I)
-----------------------------------
define ArithR > SUBW(rd::reg, rs1::reg, rs2::reg) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else writeRD(rd, SignExtend(GPR(rs1)<31:0> - GPR(rs2)<31:0>))

-----------------------------------
-- SLT   rd, rs1, rs2
-----------------------------------
define ArithR > SLT(rd::reg, rs1::reg, rs2::reg) =
{ v1  = if in32BitMode() then SignExtend(GPR(rs1)<31:0>) else GPR(rs1)
; v2  = if in32BitMode() then SignExtend(GPR(rs2)<31:0>) else GPR(rs2)
; writeRD(rd, [v1 < v2])
}

-----------------------------------
-- SLTU  rd, rs1, rs2
-----------------------------------
define ArithR > SLTU(rd::reg, rs1::reg, rs2::reg) =
{ v1  = if in32BitMode() then ZeroExtend(GPR(rs1)<31:0>) else GPR(rs1)
; v2  = if in32BitMode() then ZeroExtend(GPR(rs2)<31:0>) else GPR(rs2)
; writeRD(rd, [v1 <+ v2])
}

-----------------------------------
-- AND   rd, rs1, rs2
-----------------------------------
define ArithR > AND(rd::reg, rs1::reg, rs2::reg) =
    writeRD(rd, GPR(rs1) && GPR(rs2))

-----------------------------------
-- OR    rd, rs1, rs2
-----------------------------------
define ArithR > OR(rd::reg, rs1::reg, rs2::reg) =
    writeRD(rd, GPR(rs1) || GPR(rs2))

-----------------------------------
-- XOR   rd, rs1, rs2
-----------------------------------
define ArithR > XOR(rd::reg, rs1::reg, rs2::reg) =
    writeRD(rd, GPR(rs1) ?? GPR(rs2))

-----------------------------------
-- SLL   rd, rs1, rs2
-----------------------------------
define Shift > SLL(rd::reg, rs1::reg, rs2::reg) =
    if in32BitMode()
    then writeRD(rd, GPR(rs1) << ZeroExtend(GPR(rs2)<4:0>))
    else writeRD(rd, GPR(rs1) << ZeroExtend(GPR(rs2)<5:0>))

-----------------------------------
-- SLLW  rd, rs1, rs2   (RV64I)
-----------------------------------
define Shift > SLLW(rd::reg, rs1::reg, rs2::reg) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else writeRD(rd, SignExtend(GPR(rs1)<31:0> << ZeroExtend(GPR(rs2)<4:0>)))

-----------------------------------
-- SRL   rd, rs1, rs2
-----------------------------------
define Shift > SRL(rd::reg, rs1::reg, rs2::reg) =
    if in32BitMode()
    then writeRD(rd, ZeroExtend(GPR(rs1)<31:0> >>+ ZeroExtend(GPR(rs2)<4:0>)))
    else writeRD(rd, GPR(rs1) >>+ ZeroExtend(GPR(rs2)<5:0>))

-----------------------------------
-- SRLW  rd, rs1, rs2   (RV64I)
-----------------------------------
define Shift > SRLW(rd::reg, rs1::reg, rs2::reg) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else writeRD(rd, SignExtend(GPR(rs1)<31:0> >>+ ZeroExtend(GPR(rs2)<4:0>)))

-----------------------------------
-- SRA   rd, rs1, rs2
-----------------------------------
define Shift > SRA(rd::reg, rs1::reg, rs2::reg) =
    if in32BitMode()
    then writeRD(rd, SignExtend(GPR(rs1)<31:0> >> ZeroExtend(GPR(rs2)<4:0>)))
    else writeRD(rd, GPR(rs1) >> ZeroExtend(GPR(rs2)<5:0>))

-----------------------------------
-- SRAW  rd, rs1, rs2   (RV64I)
-----------------------------------
define Shift > SRAW(rd::reg, rs1::reg, rs2::reg) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else writeRD(rd, SignExtend(GPR(rs1)<31:0> >> ZeroExtend(GPR(rs2)<4:0>)))

---------------------------------------------------------------------------
-- Multiply and Divide
---------------------------------------------------------------------------

-----------------------------------
-- MUL   rd, rs1, rs2
-----------------------------------
define MulDiv > MUL(rd::reg, rs1::reg, rs2::reg) =
    writeRD(rd, GPR(rs1) * GPR(rs2))

-----------------------------------
-- MULH  rd, rs1, rs2
-----------------------------------
define MulDiv > MULH(rd::reg, rs1::reg, rs2::reg) =
{ v1  = if in32BitMode() then SignExtend(GPR(rs1)<31:0>) else GPR(rs1)
; v2  = if in32BitMode() then SignExtend(GPR(rs2)<31:0>) else GPR(rs2)
; prod`128 = SignExtend(v1) * SignExtend(v2)
; res = if in32BitMode() then SignExtend(prod<63:32>) else SignExtend(prod<127:64>)
; writeRD(rd, res)
}

-----------------------------------
-- MULHU rd, rs1, rs2
-----------------------------------
define MulDiv > MULHU(rd::reg, rs1::reg, rs2::reg) =
{ v1  = if in32BitMode() then ZeroExtend(GPR(rs1)<31:0>) else ZeroExtend(GPR(rs1))
; v2  = if in32BitMode() then ZeroExtend(GPR(rs2)<31:0>) else ZeroExtend(GPR(rs2))
; prod`128 = v1 * v2
; res = if in32BitMode() then ZeroExtend(prod<63:32>) else prod<127:64>
; writeRD(rd, res)
}

-----------------------------------
-- MULHSU rd, rs1, rs2
-----------------------------------
define MulDiv > MULHSU(rd::reg, rs1::reg, rs2::reg) =
{ v1  = if in32BitMode() then SignExtend(GPR(rs1)<31:0>) else SignExtend(GPR(rs1))
; v2  = if in32BitMode() then ZeroExtend(GPR(rs2)<31:0>) else ZeroExtend(GPR(rs2))
; prod`128 = v1 * v2
; res = if in32BitMode() then SignExtend(prod<63:32>) else prod<127:64>
; writeRD(rd, res)
}

-----------------------------------
-- MULW  rd, rs1, rs2
-----------------------------------
define MulDiv > MULW(rd::reg, rs1::reg, rs2::reg) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else { prod`64 = SignExtend(GPR(rs1)<31:0> * GPR(rs2)<31:0>)
         ; writeRD(rd, SignExtend(prod<31:0>))
         }

-----------------------------------
-- DIV   rd, rs1, rs2
-----------------------------------
define MulDiv > DIV(rd::reg, rs1::reg, rs2::reg) =
    if GPR(rs2) == 0x0
    then writeRD(rd, SignExtend(1`1))
    else { minus_one::regType   = SignExtend(1`1)
         ; minus_max            = 0b1 << (Size(GPR(rs1)) - 1)
         ; if GPR(rs1) == minus_max and GPR(rs2) == minus_one
           then writeRD(rd, minus_max)
           else writeRD(rd, GPR(rs1) quot GPR(rs2))
         }

-----------------------------------
-- REM   rd, rs1, rs2
-----------------------------------
define MulDiv > REM(rd::reg, rs1::reg, rs2::reg) =
    if GPR(rs2) == 0x0
    then writeRD(rd, GPR(rs1))
    else { minus_one::regType   = SignExtend(1`1)
         ; minus_max            = 0b1 << (Size(GPR(rs1)) - 1)
         ; if GPR(rs1) == minus_max and GPR(rs2) == minus_one
           then writeRD(rd, 0)
           else writeRD(rd, GPR(rs1) rem GPR(rs2))
         }

-----------------------------------
-- DIVU  rd, rs1, rs2
-----------------------------------
define MulDiv > DIVU(rd::reg, rs1::reg, rs2::reg) =
{ v1 = if in32BitMode() then ZeroExtend(GPR(rs1)<31:0>) else GPR(rs1)
; v2 = if in32BitMode() then ZeroExtend(GPR(rs2)<31:0>) else GPR(rs2)
; if v2 == 0x0
  then writeRD(rd, SignExtend(1`1))
  else writeRD(rd, v1 div v2)
}

-----------------------------------
-- REMU  rd, rs1, rs2
-----------------------------------
define MulDiv > REMU(rd::reg, rs1::reg, rs2::reg) =
    if GPR(rs2) == 0x0
    then writeRD(rd, GPR(rs1))
    else writeRD(rd, GPR(rs1) mod GPR(rs2))

-----------------------------------
-- DIVW  rd, rs1, rs2
-----------------------------------
define MulDiv > DIVW(rd::reg, rs1::reg, rs2::reg) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else { s1 = GPR(rs1)<31:0>
         ; s2 = GPR(rs2)<31:0>
         ; if s2 == 0x0
           then writeRD(rd, SignExtend(1`1))
           else { minus_one::word    = SignExtend(1`1)
                ; minus_max          = 0b1 << (Size(s1) - 1)
                ; if s1 == minus_max and s2 == minus_one
                  then writeRD(rd, SignExtend(minus_max))
                  else writeRD(rd, SignExtend(s1 quot s2))
                }
         }

-----------------------------------
-- REMW  rd, rs1, rs2
-----------------------------------
define MulDiv > REMW(rd::reg, rs1::reg, rs2::reg) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else { s1 = GPR(rs1)<31:0>
         ; s2 = GPR(rs2)<31:0>
         ; if s2 == 0x0
           then writeRD(rd, SignExtend(s1))
           else writeRD(rd, SignExtend(s1 rem s2))
         }

-----------------------------------
-- DIVUW rd, rs1, rs2
-----------------------------------
define MulDiv > DIVUW(rd::reg, rs1::reg, rs2::reg) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else { s1 = GPR(rs1)<31:0>
         ; s2 = GPR(rs2)<31:0>
         ; if s2 == 0x0
           then writeRD(rd, SignExtend(1`1))
           else writeRD(rd, SignExtend(s1 div s2))
         }

-----------------------------------
-- REMUW rd, rs1, rs2
-----------------------------------
define MulDiv > REMUW(rd::reg, rs1::reg, rs2::reg) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else { s1 = GPR(rs1)<31:0>
         ; s2 = GPR(rs2)<31:0>
         ; if s2 == 0x0
           then writeRD(rd, SignExtend(s1))
           else writeRD(rd, SignExtend(s1 mod s2))
         }

---------------------------------------------------------------------------
-- Control Transfer Instructions
---------------------------------------------------------------------------

-- Unconditional jumps

-----------------------------------
-- JAL   rd, offs
-----------------------------------
define Branch > JAL(rd::reg, imm::imm20) =
{ addr = PC + SignExtend(imm) << 1
; if addr<1:0> != 0
  then signalAddressException(E_Fetch_Misaligned, addr)
  else { writeRD(rd, PC + 4)
       ; branchTo(addr)
       }
}

-----------------------------------
-- JALR  rd, rs1, imm
-----------------------------------
define Branch > JALR(rd::reg, rs1::reg, imm::imm12) =
{ addr = (GPR(rs1) + SignExtend(imm)) && SignExtend('10')
; if addr<1:0> != 0
  then signalAddressException(E_Fetch_Misaligned, addr)
  else { writeRD(rd, PC + 4)
       ; branchTo(addr)
       }
}

-- conditional branches

-----------------------------------
-- BEQ   rs1, rs2, offs
-----------------------------------
define Branch > BEQ(rs1::reg, rs2::reg, offs::imm12) =
{ v1 = if in32BitMode() then SignExtend(GPR(rs1)<31:0>) else GPR(rs1)
; v2 = if in32BitMode() then SignExtend(GPR(rs2)<31:0>) else GPR(rs2)
; if v1 == v2
  then branchTo(PC + (SignExtend(offs) << 1))
  else noBranch(PC + 4)
}

-----------------------------------
-- BNE   rs1, rs2, offs
-----------------------------------
define Branch > BNE(rs1::reg, rs2::reg, offs::imm12) =
{ v1 = if in32BitMode() then SignExtend(GPR(rs1)<31:0>) else GPR(rs1)
; v2 = if in32BitMode() then SignExtend(GPR(rs2)<31:0>) else GPR(rs2)
; if v1 <> v2
  then branchTo(PC + (SignExtend(offs) << 1))
  else noBranch(PC + 4)
}

-----------------------------------
-- BLT   rs1, rs2, offs
-----------------------------------
define Branch > BLT(rs1::reg, rs2::reg, offs::imm12) =
{ v1 = if in32BitMode() then SignExtend(GPR(rs1)<31:0>) else GPR(rs1)
; v2 = if in32BitMode() then SignExtend(GPR(rs2)<31:0>) else GPR(rs2)
; if v1 < v2
  then branchTo(PC + (SignExtend(offs) << 1))
  else noBranch(PC + 4)
}

-----------------------------------
-- BLTU  rs1, rs2, offs
-----------------------------------
define Branch > BLTU(rs1::reg, rs2::reg, offs::imm12) =
{ v1 = if in32BitMode() then SignExtend(GPR(rs1)<31:0>) else GPR(rs1)
; v2 = if in32BitMode() then SignExtend(GPR(rs2)<31:0>) else GPR(rs2)
; if v1 <+ v2
  then branchTo(PC + (SignExtend(offs) << 1))
  else noBranch(PC + 4)
}

-----------------------------------
-- BGE   rs1, rs2, offs
-----------------------------------
define Branch > BGE(rs1::reg, rs2::reg, offs::imm12) =
{ v1 = if in32BitMode() then SignExtend(GPR(rs1)<31:0>) else GPR(rs1)
; v2 = if in32BitMode() then SignExtend(GPR(rs2)<31:0>) else GPR(rs2)
; if v1 >= v2
  then branchTo(PC + (SignExtend(offs) << 1))
  else noBranch(PC + 4)
}

-----------------------------------
-- BGEU  rs1, rs2, offs
-----------------------------------
define Branch > BGEU(rs1::reg, rs2::reg, offs::imm12) =
{ v1 = if in32BitMode() then SignExtend(GPR(rs1)<31:0>) else GPR(rs1)
; v2 = if in32BitMode() then SignExtend(GPR(rs2)<31:0>) else GPR(rs2)
; if v1 >=+ v2
  then branchTo(PC + (SignExtend(offs) << 1))
  else noBranch(PC + 4)
}

---------------------------------------------------------------------------
-- Load and Store Instructions
---------------------------------------------------------------------------

-----------------------------------
-- LW    rd, rs1, offs
-----------------------------------
define Load > LW(rd::reg, rs1::reg, offs::imm12) =
{ vAddr = GPR(rs1) + SignExtend(offs)
; match translateAddr(vAddr, Read, Data)
  { case Some(pAddr) => { val       = SignExtend(rawReadData(pAddr)<31:0>)
                        ; GPR(rd)  <- val
                        ; recordLoad(vAddr, val)
                        }
    case None        => signalAddressException(E_Load_Fault, vAddr)
  }
}

-----------------------------------
-- LWU   rd, rs1, offs  (RV64I)
-----------------------------------
define Load > LWU(rd::reg, rs1::reg, offs::imm12) =
{ if in32BitMode()
  then signalException(E_Illegal_Instr)
  else { vAddr = GPR(rs1) + SignExtend(offs)
       ; match translateAddr(vAddr, Read, Data)
         { case Some(pAddr) => { val        = ZeroExtend(rawReadData(pAddr)<31:0>)
                               ; GPR(rd)   <- val
                               ; recordLoad(vAddr, val)
                               }
           case None        => signalAddressException(E_Load_Fault, vAddr)
         }
       }
}

-----------------------------------
-- LH    rd, rs1, offs
-----------------------------------
define Load > LH(rd::reg, rs1::reg, offs::imm12) =
{ vAddr = GPR(rs1) + SignExtend(offs)
; match translateAddr(vAddr, Read, Data)
  { case Some(pAddr) => { val       = SignExtend(rawReadData(pAddr)<15:0>)
                        ; GPR(rd)  <- val
                        ; recordLoad(vAddr, val)
                        }
    case None        => signalAddressException(E_Load_Fault, vAddr)
  }
}

-----------------------------------
-- LHU   rd, rs1, offs
-----------------------------------
define Load > LHU(rd::reg, rs1::reg, offs::imm12) =
{ vAddr = GPR(rs1) + SignExtend(offs)
; match translateAddr(vAddr, Read, Data)
  { case Some(pAddr) => { val       = ZeroExtend(rawReadData(pAddr)<15:0>)
                        ; GPR(rd)  <- val
                        ; recordLoad(vAddr, val)
                        }
    case None        => signalAddressException(E_Load_Fault, vAddr)
  }
}

-----------------------------------
-- LB    rd, rs1, offs
-----------------------------------
define Load > LB(rd::reg, rs1::reg, offs::imm12) =
{ vAddr = GPR(rs1) + SignExtend(offs)
; match translateAddr(vAddr, Read, Data)
  { case Some(pAddr) => { val       = SignExtend(rawReadData(pAddr)<7:0>)
                        ; GPR(rd)  <- val
                        ; recordLoad(vAddr, val)
                        }
    case None        => signalAddressException(E_Load_Fault, vAddr)
  }
}

-----------------------------------
-- LBU   rd, rs1, offs
-----------------------------------
define Load > LBU(rd::reg, rs1::reg, offs::imm12) =
{ vAddr = GPR(rs1) + SignExtend(offs)
; match translateAddr(vAddr, Read, Data)
  { case Some(pAddr) => { val       = ZeroExtend(rawReadData(pAddr)<7:0>)
                        ; GPR(rd)  <- val
                        ; recordLoad(vAddr, val)
                        }
    case None        => signalAddressException(E_Load_Fault, vAddr)
  }
}

-----------------------------------
-- LD    rd, rs1, offs  (RV64I)
-----------------------------------
define Load > LD(rd::reg, rs1::reg, offs::imm12) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else { vAddr = GPR(rs1) + SignExtend(offs)
         ; match translateAddr(vAddr, Read, Data)
           { case Some(pAddr) => { val      = rawReadData(pAddr)
                                 ; GPR(rd) <- val
                                 ; recordLoad(vAddr, val)
                                 }
             case None        => signalAddressException(E_Load_Fault, vAddr)
           }
         }

-----------------------------------
-- SW    rs1, rs2, offs
-----------------------------------
define Store > SW(rs1::reg, rs2::reg, offs::imm12) =
{ vAddr = GPR(rs1) + SignExtend(offs)
; match translateAddr(vAddr, Write, Data)
  { case Some(pAddr) => { data = GPR(rs2)
                        ; rawWriteData(pAddr, data, 4)
                        ; recordStore(vAddr, data, 4)
                        }
    case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
  }
}

-----------------------------------
-- SH    rs1, rs2, offs
-----------------------------------
define Store > SH(rs1::reg, rs2::reg, offs::imm12) =
{ vAddr = GPR(rs1) + SignExtend(offs)
; match translateAddr(vAddr, Write, Data)
  { case Some(pAddr) => { data = GPR(rs2)
                        ; rawWriteData(pAddr, data, 2)
                        ; recordStore(vAddr, data, 2)
                        }
    case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
  }
}

-----------------------------------
-- SB    rs1, rs2, offs
-----------------------------------
define Store > SB(rs1::reg, rs2::reg, offs::imm12) =
{ vAddr = GPR(rs1) + SignExtend(offs)
; match translateAddr(vAddr, Write, Data)
  { case Some(pAddr) => { data = GPR(rs2)
                        ; rawWriteData(pAddr, data, 1)
                        ; recordStore(vAddr, data, 1)
                        }
    case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
  }
}

-----------------------------------
-- SD    rs1, rs2, offs (RV64I)
-----------------------------------
define Store > SD(rs1::reg, rs2::reg, offs::imm12) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else { vAddr = GPR(rs1) + SignExtend(offs)
         ; match translateAddr(vAddr, Write, Data)
           { case Some(pAddr) => { data = GPR(rs2)
                                 ; rawWriteData(pAddr, data, 8)
                                 ; recordStore(vAddr, data, 8)
                                 }
             case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
           }
         }

---------------------------------------------------------------------------
-- Memory model
---------------------------------------------------------------------------

-----------------------------------
-- FENCE rd, rs1, pred, succ
-----------------------------------
define FENCE(rd::reg, rs1::reg, pred::bits(4), succ::bits(4)) = nothing

-----------------------------------
-- FENCE.I rd, rs1, imm
-----------------------------------
define FENCE_I(rd::reg, rs1::reg, imm::imm12) = nothing

-- Atomics --

-----------------------------------
-- LR.W [aq,rl] rd, rs1
-----------------------------------
define AMO > LR_W(aq::amo, rl::amo, rd::reg, rs1::reg) =
{ vAddr = GPR(rs1)
; if vAddr<1:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, Read, Data)
       { case Some(pAddr) => { writeRD(rd, SignExtend(rawReadData(pAddr)<31:0>))
                             ; ReserveLoad  <- Some(vAddr)
                             }
         case None        => signalAddressException(E_Load_Fault, vAddr)
       }
}

-----------------------------------
-- LR.D [aq,rl] rd, rs1
-----------------------------------
define AMO > LR_D(aq::amo, rl::amo, rd::reg, rs1::reg) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else { vAddr = GPR(rs1)
         ; if vAddr<2:0> != 0
           then signalAddressException(E_AMO_Misaligned, vAddr)
           else match translateAddr(vAddr, Read, Data)
                { case Some(pAddr) => { writeRD(rd, rawReadData(pAddr))
                                      ; ReserveLoad <- Some(vAddr)
                                      }
                  case None        => signalAddressException(E_Load_Fault, vAddr)
                }
         }

-----------------------------------
-- SC.W [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > SC_W(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<1:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else if not matchLoadReservation(vAddr)
       then writeRD(rd, 1)
       else match translateAddr(vAddr, Write, Data)
            { case Some(pAddr) => { data = GPR(rs2)
                                  ; rawWriteData(pAddr, data, 4)
                                  ; recordStore(vAddr, data, 4)
                                  ; writeRD(rd, 0)
                                  ; ReserveLoad  <- None
                                  }
              case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
            }
}

-----------------------------------
-- SC.D [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > SC_D(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
    if in32BitMode()
    then signalException(E_Illegal_Instr)
    else { vAddr = GPR(rs1)
         ; if vAddr<2:0> != 0
           then signalAddressException(E_AMO_Misaligned, vAddr)
           else if not matchLoadReservation(vAddr)
                then writeRD(rd, 1)
                else match translateAddr(vAddr, Write, Data)
                     { case Some(pAddr) => { data = GPR(rs2)
                                           ; rawWriteData(pAddr, data, 4)
                                           ; recordStore(vAddr, data, 4)
                                           ; writeRD(rd, 0)
                                           ; ReserveLoad  <- None
                                           }
                       case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
                     }
         }

-----------------------------------
-- AMOSWAP.W [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOSWAP_W(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<1:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = SignExtend(rawReadData(pAddr)<31:0>)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; rawWriteData(pAddr, data, 4)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, data, 4)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}

-----------------------------------
-- AMOSWAP.D [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOSWAP_D(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<2:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = rawReadData(pAddr)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; rawWriteData(pAddr, data, 8)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, data, 8)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}

-----------------------------------
-- AMOADD.W [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOADD_W(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<1:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = SignExtend(rawReadData(pAddr)<31:0>)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; val  = data + memv
                             ; rawWriteData(pAddr, val, 4)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, val, 4)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}

-----------------------------------
-- AMOADD.D [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOADD_D(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<2:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = rawReadData(pAddr)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; val  = data + memv
                             ; rawWriteData(pAddr, val, 8)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, val, 8)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}

-----------------------------------
-- AMOXOR.W [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOXOR_W(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<1:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = SignExtend(rawReadData(pAddr)<31:0>)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; val  = data ?? memv
                             ; rawWriteData(pAddr, val, 4)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, val, 4)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}

-----------------------------------
-- AMOXOR.D [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOXOR_D(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<2:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = rawReadData(pAddr)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; val  = data ?? memv
                             ; rawWriteData(pAddr, val, 8)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, val, 8)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}

-----------------------------------
-- AMOAND.W [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOAND_W(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<1:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = SignExtend(rawReadData(pAddr)<31:0>)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; val  = data && memv
                             ; rawWriteData(pAddr, val, 4)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, val, 4)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}

-----------------------------------
-- AMOAND.D [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOAND_D(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<2:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = rawReadData(pAddr)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; val  = data && memv
                             ; rawWriteData(pAddr, val, 8)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, val, 8)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}

-----------------------------------
-- AMOOR.W [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOOR_W(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<1:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = SignExtend(rawReadData(pAddr)<31:0>)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; val  = data || memv
                             ; rawWriteData(pAddr, val, 4)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, val, 4)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}

-----------------------------------
-- AMOOR.D [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOOR_D(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<2:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = rawReadData(pAddr)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; val  = data || memv
                             ; rawWriteData(pAddr, val, 8)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, val, 8)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}

-----------------------------------
-- AMOMIN.W [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOMIN_W(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<1:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = SignExtend(rawReadData(pAddr)<31:0>)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; val  = SignedMin(data, memv)
                             ; rawWriteData(pAddr, val, 4)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, val, 4)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}

-----------------------------------
-- AMOMIN.D [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOMIN_D(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<2:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = rawReadData(pAddr)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; val  = SignedMin(data, memv)
                             ; rawWriteData(pAddr, val, 8)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, val, 8)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}

-----------------------------------
-- AMOMAX.W [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOMAX_W(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<1:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = SignExtend(rawReadData(pAddr)<31:0>)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; val  = SignedMax(data, memv)
                             ; rawWriteData(pAddr, val, 4)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, val, 4)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}

-----------------------------------
-- AMOMAX.D [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOMAX_D(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<2:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = rawReadData(pAddr)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; val  = SignedMax(data, memv)
                             ; rawWriteData(pAddr, val, 8)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, val, 8)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}

-----------------------------------
-- AMOMINU.W [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOMINU_W(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<1:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = SignExtend(rawReadData(pAddr)<31:0>)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; val  = Min(data, memv)
                             ; rawWriteData(pAddr, val, 4)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, val, 4)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}

-----------------------------------
-- AMOMINU.D [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOMINU_D(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<2:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = rawReadData(pAddr)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; val  = Min(data, memv)
                             ; rawWriteData(pAddr, val, 8)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, val, 8)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}

-----------------------------------
-- AMOMAXU.W [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOMAXU_W(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<1:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = SignExtend(rawReadData(pAddr)<31:0>)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; val  = Max(data, memv)
                             ; rawWriteData(pAddr, val, 4)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, val, 4)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}

-----------------------------------
-- AMOMAXU.D [aq,rl] rd, rs1, rs2
-----------------------------------
define AMO > AMOMAXU_D(aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
{ vAddr = GPR(rs1)
; if vAddr<2:0> != 0
  then signalAddressException(E_AMO_Misaligned, vAddr)
  else match translateAddr(vAddr, ReadWrite, Data)
       { case Some(pAddr) => { memv = rawReadData(pAddr)
                             ; data = GPR(rs2)
                             ; GPR(rd) <- memv
                             ; val  = Max(data, memv)
                             ; rawWriteData(pAddr, val, 8)
                             ; recordLoad(vAddr, memv)
                             ; recordStore(vAddr, val, 8)
                             }
         case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
       }
}


---------------------------------------------------------------------------
-- Floating Point Instructions (Single Precision)
---------------------------------------------------------------------------

-- Load/Store

-----------------------------------
-- FLW   rd, rs2, offs
-----------------------------------

define FPLoad > FLW(rd::reg, rs1::reg, offs::imm12) =
{ vAddr = GPR(rs1) + SignExtend(offs)
; match translateAddr(vAddr, Read, Data)
  { case Some(pAddr) => { val       = rawReadData(pAddr)<31:0>
                        ; FPRS(rd) <- val
                        ; recordLoad(vAddr, ZeroExtend(val))
                        }
    case None        => signalAddressException(E_Load_Fault, vAddr)
  }
}

-----------------------------------
-- FSW   rs1, rs2, offs
-----------------------------------

define FPStore > FSW(rs1::reg, rs2::reg, offs::imm12) =
{ vAddr = GPR(rs1) + SignExtend(offs)
; match translateAddr(vAddr, Write, Data)
  { case Some(pAddr) => { data = FPRS(rs2)
                        ; rawWriteData(pAddr, ZeroExtend(data), 4)
                        ; recordStore(vAddr, ZeroExtend(data), 4)
                        }
    case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
  }
}

-- Computational

-- TODO: Check for underflow after all rounding

-----------------------------------
-- FADD.S   rd, rs1, rs2
-----------------------------------

define FArith > FADD_S(rd::reg, rs1::reg, rs2::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRS(rd, FP32_Add(r, FPRS(rs1), FPRS(rs2)))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FSUB.S   rd, rs1, rs2
-----------------------------------

define FArith > FSUB_S(rd::reg, rs1::reg, rs2::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRS(rd, FP32_Sub(r, FPRS(rs1), FPRS(rs2)))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FMUL.S   rd, rs1, rs2
-----------------------------------

define FArith > FMUL_S(rd::reg, rs1::reg, rs2::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRS(rd, FP32_Mul(r, FPRS(rs1), FPRS(rs2)))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FDIV.S   rd, rs1, rs2
-----------------------------------

define FArith > FDIV_S(rd::reg, rs1::reg, rs2::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRS(rd, FP32_Div(r, FPRS(rs1), FPRS(rs2)))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FSQRT.S   rd, rs
-----------------------------------

define FArith > FSQRT_S(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRS(rd, FP32_Sqrt(r, FPRS(rs)))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FMIN.S    rd, rs1, rs2
-----------------------------------
define FArith > FMIN_S(rd::reg, rs1::reg, rs2::reg) =
{ f1  = FPRS(rs1)
; f2  = FPRS(rs2)
; res = match FP32_Compare(f1, f2)
        { case FP_LT   => f1
          case FP_EQ   => f1
          case FP_GT   => f2
          case FP_UN   => if (   (FP32_IsSignalingNan(f1) or FP32_IsSignalingNan(f2))
                              or (f1 == RV32_CanonicalNan and f2 == RV32_CanonicalNan))
                          then RV32_CanonicalNan
                          else -- either f1 or f2 should be a quiet NaN
                              if f1 == RV32_CanonicalNan then f2 else f1
        }
; writeFPRS(rd, res)
}

-----------------------------------
-- FMAX.S    rd, rs1, rs2
-----------------------------------
define FArith > FMAX_S(rd::reg, rs1::reg, rs2::reg) =
{ f1  = FPRS(rs1)
; f2  = FPRS(rs2)
; res = match FP32_Compare(f1, f2)
        { case FP_LT   => f2
          case FP_EQ   => f2
          case FP_GT   => f1
          case FP_UN   => if (   (FP32_IsSignalingNan(f1) or FP32_IsSignalingNan(f2))
                              or (f1 == RV32_CanonicalNan and f2 == RV32_CanonicalNan))
                          then RV32_CanonicalNan
                          else -- either f1 or f2 should be a quiet NaN
                              if f1 == RV32_CanonicalNan then f2 else f1
        }
; writeFPRS(rd, res)
}

-----------------------------------
-- FMADD.S   rd, rs1, rs2, rs3
-----------------------------------

define FArith > FMADD_S(rd::reg, rs1::reg, rs2::reg, rs3::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRS(rd, FP32_Add(r, FP32_Mul(r, FPRS(rs1), FPRS(rs2)), FPRS(rs3)))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FMSUB.S   rd, rs1, rs2, rs3
-----------------------------------

define FArith > FMSUB_S(rd::reg, rs1::reg, rs2::reg, rs3::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRS(rd, FP32_Sub(r, FP32_Mul(r, FPRS(rs1), FPRS(rs2)), FPRS(rs3)))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FNMADD.S   rd, rs1, rs2, rs3
-----------------------------------

define FArith > FNMADD_S(rd::reg, rs1::reg, rs2::reg, rs3::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRS(rd, FP32_Neg(FP32_Add(r, FP32_Mul(r, FPRS(rs1), FPRS(rs2)), FPRS(rs3))))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FNMSUB.S   rd, rs1, rs2, rs3
-----------------------------------

define FArith > FNMSUB_S(rd::reg, rs1::reg, rs2::reg, rs3::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRS(rd, FP32_Neg(FP32_Sub(r, FP32_Mul(r, FPRS(rs1), FPRS(rs2)), FPRS(rs3))))
    case None    => signalException(E_Illegal_Instr)
  }
}

-- Conversions

-----------------------------------
-- FCVT.S.W   rd, rs
-----------------------------------

define FConv > FCVT_S_W(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRS(rd, FP32_FromInt(r, [GPR(rs)<31:0>]::int))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FCVT.S.WU  rd, rs
-----------------------------------

define FConv > FCVT_S_WU(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRS(rd, FP32_FromInt(r, [0`1 : GPR(rs)<31:0>]::int))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FCVT.W.S   rd, rs
-----------------------------------

define FConv > FCVT_W_S(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => { inp = FPRS(rs)
                    ; val = ValOf(FP32_ToInt(r, inp))
                    ; res = if   FP32_IsNan(inp) or inp == FP32_PosInf
                            then [0n2 ** 31 - 1]
                            else if inp == FP32_NegInf
                            then -[0n2 ** 31]
                            else if val > 2 ** 31 - 1
                            then [0n2 ** 31 - 1]
                            else if val < -2 ** 31
                            then -[0n2 ** 31]
                            else [val]
                    ; writeRD(rd, res)
                    }
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FCVT.WU.S  rd, rs
-----------------------------------

define FConv > FCVT_WU_S(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => { inp = FPRS(rs)
                    ; val = ValOf(FP32_ToInt(r, inp))
                    ; res = if   FP32_IsNan(inp) or inp == FP32_PosInf
                            then [0n2 ** 32 - 1]
                            else if inp == FP32_NegInf
                            then 0x0
                            else if val > 2 ** 32 - 1
                            then [0n2 ** 32 - 1]
                            else if val < 0
                            then 0x0
                            else [val]
                    ; writeRD(rd, res)
                    }
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FCVT.S.L   rd, rs
-----------------------------------

define FConv > FCVT_S_L(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRS(rd, FP32_FromInt(r, [GPR(rs)]::int))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FCVT.S.LU  rd, rs
-----------------------------------

define FConv > FCVT_S_LU(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRS(rd, FP32_FromInt(r, [0`1 : GPR(rs)]::int))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FCVT.L.S   rd, rs
-----------------------------------

define FConv > FCVT_L_S(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => { inp = FPRS(rs)
                    ; val = ValOf(FP32_ToInt(r, inp))
                    ; res = if   FP32_IsNan(inp) or inp == FP32_PosInf
                            then [0n2 ** 63 - 1]
                            else if inp == FP32_NegInf
                            then -[0n2 ** 63]
                            else if val > 2 ** 63 - 1
                            then [0n2 ** 63 - 1]
                            else if val < -2 ** 63
                            then -[0n2 ** 63]
                            else [val]
                    ; writeRD(rd, res)
                    }
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FCVT.LU.S  rd, rs
-----------------------------------

define FConv > FCVT_LU_S(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => { inp = FPRS(rs)
                    ; val = ValOf(FP32_ToInt(r, inp))
                    ; res = if   FP32_IsNan(inp) or inp == FP32_PosInf
                            then [0n2 ** 64 - 1]
                            else if inp == FP32_NegInf
                            then 0x0
                            else if val > 2 ** 64 - 1
                            then [0n2 ** 64 - 1]
                            else if val < 0
                            then 0x0
                            else [val]
                    ; writeRD(rd, res)
                    }
    case None    => signalException(E_Illegal_Instr)
  }
}

-- Sign injection

-----------------------------------
-- FSGNJ.S   rd, rs
-----------------------------------

define FConv > FSGNJ_S(rd::reg, rs1::reg, rs2::reg) =
{ f1 = FPRS(rs1)
; f2 = FPRS(rs2)
; writeFPRS(rd, ([FP32_Sign(f2)]::bits(1)):f1<30:0>)
}

-----------------------------------
-- FSGNJN.S  rd, rs
-----------------------------------

define FConv > FSGNJN_S(rd::reg, rs1::reg, rs2::reg) =
{ f1 = FPRS(rs1)
; f2 = FPRS(rs2)
; writeFPRS(rd, ([!FP32_Sign(f2)]::bits(1)):f1<30:0>)
}

-----------------------------------
-- FSGNJX.S  rd, rs
-----------------------------------

define FConv > FSGNJX_S(rd::reg, rs1::reg, rs2::reg) =
{ f1 = FPRS(rs1)
; f2 = FPRS(rs2)
; writeFPRS(rd, ([FP32_Sign(f2)]::bits(1) ?? [FP32_Sign(f1)]::bits(1)) : f1<30:0>)
}

-- Movement

-----------------------------------
-- FMV.X.S   rd, rs
-----------------------------------

define FConv > FMV_X_S(rd::reg, rs::reg) =
    GPR(rd) <- SignExtend(FPRS(rs))

-----------------------------------
-- FMV.S.X   rd, rs
-----------------------------------

define FConv > FMV_S_X(rd::reg, rs::reg) =
    writeFPRS(rd, GPR(rs)<31:0>)

-- Comparisons

-----------------------------------
-- FEQ.S   rd, rs
-----------------------------------

define FArith > FEQ_S(rd::reg, rs1::reg, rs2::reg) =
{ f1  = FPRS(rs1)
; f2  = FPRS(rs2)
; if FP32_IsSignalingNan(f1) or FP32_IsSignalingNan(f2)
  then { writeRD(rd, 0x0)
       ; setFP_Invalid()
       }
  else { res = match FP32_Compare(f1, f2)
               { case FP_LT => 0x0
                 case FP_EQ => 0x1
                 case FP_GT => 0x0
                 case FP_UN => 0x0
               }
       ; writeRD(rd, res)
       }
}

-----------------------------------
-- FLT.S   rd, rs
-----------------------------------

define FArith > FLT_S(rd::reg, rs1::reg, rs2::reg) =
{ f1  = FPRS(rs1)
; f2  = FPRS(rs2)
; if   FP32_IsNan(f1) or FP32_IsNan(f2)
  then { writeRD(rd, 0x0)
       ; setFP_Invalid()
       }
  else { res = match FP32_Compare(f1, f2)
               { case FP_LT => 0x1
                 case FP_EQ => 0x0
                 case FP_GT => 0x0
                 case FP_UN => 0x0
               }
       ; writeRD(rd, res)
       }
  }

-----------------------------------
-- FLE.S   rd, rs
-----------------------------------

define FArith > FLE_S(rd::reg, rs1::reg, rs2::reg) =
{ f1  = FPRS(rs1)
; f2  = FPRS(rs2)
; if   FP32_IsNan(f1) or FP32_IsNan(f2)
  then { writeRD(rd, 0x0)
       ; setFP_Invalid()
       }
  else { res = match FP32_Compare(f1, f2)
               { case FP_LT => 0x1
                 case FP_EQ => 0x1
                 case FP_GT => 0x0
                 case FP_UN => 0x0
               }
       ; writeRD(rd, res)
       }
}

-- Classification

-----------------------------------
-- FCLASS.S  rd, rs
-----------------------------------

define FConv > FCLASS_S(rd::reg, rs::reg) =
{ var ret = 0x0`10
; val = FPRS(rs)
; ret<0> <- val == FP32_NegInf
; ret<1> <- FP32_Sign(val) and FP32_IsNormal(val)
; ret<2> <- FP32_Sign(val) and FP32_IsSubnormal(val)
; ret<3> <- val == FP32_NegZero
; ret<4> <- val == FP32_PosZero
; ret<5> <- !FP32_Sign(val) and FP32_IsSubnormal(val)
; ret<6> <- !FP32_Sign(val) and FP32_IsNormal(val)
; ret<7> <- val == FP32_PosInf
; ret<8> <- FP32_IsSignalingNan(val)
; ret<9> <- val == RV32_CanonicalNan
; writeRD(rd, ZeroExtend(ret))
}

---------------------------------------------------------------------------
-- Floating Point Instructions (Double Precision)
---------------------------------------------------------------------------

-- Load/Store

-----------------------------------
-- FLD   rd, rs2, offs
-----------------------------------

define FPLoad > FLD(rd::reg, rs1::reg, offs::imm12) =
{ vAddr = GPR(rs1) + SignExtend(offs)
; match translateAddr(vAddr, Read, Data)
  { case Some(pAddr) => { val       = rawReadData(pAddr)
                        ; FPRD(rd) <- val
                        ; recordLoad(vAddr, val)
                        }
    case None        => signalAddressException(E_Load_Fault, vAddr)
  }
}

-----------------------------------
-- FSD   rs1, rs2, offs
-----------------------------------

define FPStore > FSD(rs1::reg, rs2::reg, offs::imm12) =
{ vAddr = GPR(rs1) + SignExtend(offs)
; match translateAddr(vAddr, Write, Data)
  { case Some(pAddr) => { data = FPRD(rs2)
                        ; rawWriteData(pAddr, data, 8)
                        ; recordStore(vAddr, data, 8)
                        }
    case None        => signalAddressException(E_Store_AMO_Fault, vAddr)
  }
}

-- Computational

-- TODO: Check for underflow after all rounding

-----------------------------------
-- FADD.D   rd, rs1, rs2
-----------------------------------

define FArith > FADD_D(rd::reg, rs1::reg, rs2::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRD(rd, FP64_Add(r, FPRD(rs1), FPRD(rs2)))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FSUB.D   rd, rs1, rs2
-----------------------------------

define FArith > FSUB_D(rd::reg, rs1::reg, rs2::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRD(rd, FP64_Sub(r, FPRD(rs1), FPRD(rs2)))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FMUL.D   rd, rs1, rs2
-----------------------------------

define FArith > FMUL_D(rd::reg, rs1::reg, rs2::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRD(rd, FP64_Mul(r, FPRD(rs1), FPRD(rs2)))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FDIV.D   rd, rs1, rs2
-----------------------------------

define FArith > FDIV_D(rd::reg, rs1::reg, rs2::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRD(rd, FP64_Div(r, FPRD(rs1), FPRD(rs2)))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FSQRT.D   rd, rs
-----------------------------------

define FArith > FSQRT_D(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRD(rd, FP64_Sqrt(r, FPRD(rs)))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FMIN.D    rd, rs1, rs2
-----------------------------------
define FArith > FMIN_D(rd::reg, rs1::reg, rs2::reg) =
{ f1 = FPRD(rs1)
; f2 = FPRD(rs2)
; res = match FP64_Compare(f1, f2)
        { case FP_LT => f1
          case FP_EQ => f1
          case FP_GT => f2
          case FP_UN => if (   (FP64_IsSignalingNan(f1) or FP64_IsSignalingNan(f2))
                            or (f1 == RV64_CanonicalNan and f2 == RV64_CanonicalNan))
                        then RV64_CanonicalNan
                        else -- either f1 or f2 should be a quiet NaN
                            if f1 == RV64_CanonicalNan then f2 else f1

        }
; writeFPRD(rd, res)
}

-----------------------------------
-- FMAX.D    rd, rs1, rs2
-----------------------------------
define FArith > FMAX_D(rd::reg, rs1::reg, rs2::reg) =
{ f1 = FPRD(rs1)
; f2 = FPRD(rs2)
; res = match FP64_Compare(f1, f2)
        { case FP_LT => f2
          case FP_EQ => f2
          case FP_GT => f1
          case FP_UN => if (   (FP64_IsSignalingNan(f1) or FP64_IsSignalingNan(f2))
                            or (f1 == RV64_CanonicalNan and f2 == RV64_CanonicalNan))
                        then RV64_CanonicalNan
                        else -- either f1 or f2 should be a quiet NaN
                            if f1 == RV64_CanonicalNan then f2 else f1
  }
; writeFPRD(rd, res)
}

-----------------------------------
-- FMADD.D   rd, rs1, rs2, rs3
-----------------------------------

define FArith > FMADD_D(rd::reg, rs1::reg, rs2::reg, rs3::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRD(rd, FP64_Add(r, FP64_Mul(r, FPRD(rs1), FPRD(rs2)), FPRD(rs3)))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FMSUB.D   rd, rs1, rs2, rs3
-----------------------------------

define FArith > FMSUB_D(rd::reg, rs1::reg, rs2::reg, rs3::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRD(rd, FP64_Sub(r, FP64_Mul(r, FPRD(rs1), FPRD(rs2)), FPRD(rs3)))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FNMADD.D   rd, rs1, rs2, rs3
-----------------------------------

define FArith > FNMADD_D(rd::reg, rs1::reg, rs2::reg, rs3::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRD(rd, FP64_Neg(FP64_Add(r, FP64_Mul(r, FPRD(rs1), FPRD(rs2)), FPRD(rs3))))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FNMSUB.D   rd, rs1, rs2, rs3
-----------------------------------

define FArith > FNMSUB_D(rd::reg, rs1::reg, rs2::reg, rs3::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRD(rd, FP64_Neg(FP64_Sub(r, FP64_Mul(r, FPRD(rs1), FPRD(rs2)), FPRD(rs3))))
    case None    => signalException(E_Illegal_Instr)
  }
}

-- Conversions

-----------------------------------
-- FCVT.D.W   rd, rs
-----------------------------------

define FConv > FCVT_D_W(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRD(rd, FP64_FromInt(r, [GPR(rs)<31:0>]::int))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FCVT.D.WU  rd, rs
-----------------------------------

define FConv > FCVT_D_WU(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRD(rd, FP64_FromInt(r, [0`1 : GPR(rs)<31:0>]::int))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FCVT.W.D   rd, rs
-----------------------------------

define FConv > FCVT_W_D(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => { inp = FPRD(rs)
                    ; val = ValOf(FP64_ToInt(r, inp))
                    ; res = if   FP64_IsNan(inp) or inp == FP64_PosInf
                            then [0n2 ** 31 - 1]
                            else if inp == FP64_NegInf
                            then -[0n2 ** 31]
                            else if val > 2 ** 31 - 1
                            then [0n2 ** 31 - 1]
                            else if val < -2 ** 31
                            then -[0n2 ** 31]
                            else [val]
                    ; writeRD(rd, res)
                    }
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FCVT.WU.D  rd, rs
-----------------------------------

define FConv > FCVT_WU_D(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => { inp = FPRD(rs)
                    ; val = ValOf(FP64_ToInt(r, inp))
                    ; res = if   FP64_IsNan(inp) or inp == FP64_PosInf
                            then [0n2 ** 32 - 1]
                            else if inp == FP64_NegInf
                            then 0x0
                            else if val > 2 ** 32 - 1
                            then [0n2 ** 32 - 1]
                            else if val < 0
                            then 0x0
                            else [val]
                    ; writeRD(rd, res)
                    }
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FCVT.D.L   rd, rs
-----------------------------------

define FConv > FCVT_D_L(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRD(rd, FP64_FromInt(r, [GPR(rs)]::int))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FCVT.D.LU  rd, rs
-----------------------------------

define FConv > FCVT_D_LU(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRD(rd, FP64_FromInt(r, [0`1 : GPR(rs)]::int))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FCVT.L.D   rd, rs
-----------------------------------

define FConv > FCVT_L_D(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => { inp = FPRD(rs)
                    ; val = ValOf(FP64_ToInt(r, inp))
                    ; res = if   FP64_IsNan(inp) or inp == FP64_PosInf
                            then [0n2 ** 63 - 1]
                            else if inp == FP64_NegInf
                            then -[0n2 ** 63]
                            else if val > 2 ** 63 - 1
                            then [0n2 ** 63 - 1]
                            else if val < -2 ** 63
                            then -[0n2 ** 63]
                            else [val]
                    ; writeRD(rd, res)
                    }
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FCVT.LU.D  rd, rs
-----------------------------------

define FConv > FCVT_LU_D(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => { inp = FPRD(rs)
                    ; val = ValOf(FP64_ToInt(r, inp))
                    ; res = if   FP64_IsNan(inp) or inp == FP64_PosInf
                            then [0n2 ** 64 - 1]
                            else if inp == FP64_NegInf
                            then 0x0
                            else if val > 2 ** 64 - 1
                            then [0n2 ** 64 - 1]
                            else if val < 0
                            then 0x0
                            else [val]
                    ; writeRD(rd, res)
                    }
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FCVT.S.D  rd, rs
-----------------------------------

define FConv > FCVT_S_D(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRS(rd, FP64_ToFP32(r, FPRD(rs)))
    case None    => signalException(E_Illegal_Instr)
  }
}

-----------------------------------
-- FCVT.D.S  rd, rs
-----------------------------------

define FConv > FCVT_D_S(rd::reg, rs::reg, fprnd::fprnd) =
{ match round(fprnd)
  { case Some(r) => writeFPRD(rd, FP32_ToFP64(FPRS(rs)))
    case None    => signalException(E_Illegal_Instr)
  }
}

-- Sign injection

-----------------------------------
-- FSGNJ.D  rd, rs
-----------------------------------

define FConv > FSGNJ_D(rd::reg, rs1::reg, rs2::reg) =
{ f1 = FPRD(rs1)
; f2 = FPRD(rs2)
; writeFPRD(rd, ([FP64_Sign(f2)]::bits(1)):f1<62:0>)
}

-----------------------------------
-- FSGNJN.D  rd, rs
-----------------------------------

define FConv > FSGNJN_D(rd::reg, rs1::reg, rs2::reg) =
{ f1 = FPRD(rs1)
; f2 = FPRD(rs2)
; writeFPRD(rd, ([!FP64_Sign(f2)]::bits(1)):f1<62:0>)
}

-----------------------------------
-- FSGNJX.D  rd, rs
-----------------------------------

define FConv > FSGNJX_D(rd::reg, rs1::reg, rs2::reg) =
{ f1 = FPRD(rs1)
; f2 = FPRD(rs2)
; writeFPRD(rd, ([FP64_Sign(f2)]::bits(1) ?? [FP64_Sign(f1)]::bits(1)) : f1<62:0>)
}

-- Movement

-----------------------------------
-- FMV.X.D   rd, rs
-----------------------------------

define FConv > FMV_X_D(rd::reg, rs::reg) =
    GPR(rd) <- SignExtend(FPRD(rs))

-----------------------------------
-- FMV.D.X   rd, rs
-----------------------------------

define FConv > FMV_D_X(rd::reg, rs::reg) =
    writeFPRD(rd, GPR(rs))

-- Comparisons

-----------------------------------
-- FEQ.D   rd, rs
-----------------------------------

define FArith > FEQ_D(rd::reg, rs1::reg, rs2::reg) =
{ f1  = FPRD(rs1)
; f2  = FPRD(rs2)
; if FP64_IsSignalingNan(f1) or FP64_IsSignalingNan(f2)
  then { writeRD(rd, 0x0)
       ; setFP_Invalid()
       }
  else { res = match FP64_Compare(f1, f2)
               { case FP_LT => 0x0
                 case FP_EQ => 0x1
                 case FP_GT => 0x0
                 case FP_UN => 0x0
               }
       ; writeRD(rd, res)
       }
}

-----------------------------------
-- FLT.D   rd, rs
-----------------------------------

define FArith > FLT_D(rd::reg, rs1::reg, rs2::reg) =
{ f1  = FPRD(rs1)
; f2  = FPRD(rs2)
; if   FP64_IsNan(f1) or FP64_IsNan(f2)
  then { writeRD(rd, 0x0)
       ; setFP_Invalid()
       }
  else { res = match FP64_Compare(f1, f2)
               { case FP_LT => 0x1
                 case FP_EQ => 0x0
                 case FP_GT => 0x0
                 case FP_UN => 0x0
               }
       ; writeRD(rd, res)
       }
}

-----------------------------------
-- FLE.D   rd, rs
-----------------------------------

define FArith > FLE_D(rd::reg, rs1::reg, rs2::reg) =
{ f1  = FPRD(rs1)
; f2  = FPRD(rs2)
; if   FP64_IsNan(f1) or FP64_IsNan(f2)
  then { writeRD(rd, 0x0)
       ; setFP_Invalid()
       }
  else { res = match FP64_Compare(f1, f2)
               { case FP_LT => 0x1
                 case FP_EQ => 0x1
                 case FP_GT => 0x0
                 case FP_UN => 0x0
               }
       ; writeRD(rd, res)
       }
}

-- Classification

-----------------------------------
-- FCLASS.D  rd, rs
-----------------------------------

define FConv > FCLASS_D(rd::reg, rs::reg) =
{ var ret = 0x0`10
; val = FPRD(rs)
; ret<0> <- val == FP64_NegInf
; ret<1> <- FP64_Sign(val) and FP64_IsNormal(val)
; ret<2> <- FP64_Sign(val) and FP64_IsSubnormal(val)
; ret<3> <- val == FP64_NegZero
; ret<4> <- val == FP64_PosZero
; ret<5> <- !FP64_Sign(val) and FP64_IsSubnormal(val)
; ret<6> <- !FP64_Sign(val) and FP64_IsNormal(val)
; ret<7> <- val == FP64_PosInf
; ret<8> <- FP64_IsSignalingNan(val)
; ret<9> <- val == RV64_CanonicalNan
; writeRD(rd, ZeroExtend(ret))
}

---------------------------------------------------------------------------
-- System Instructions
---------------------------------------------------------------------------

-----------------------------------
-- ECALL
-----------------------------------
define System > ECALL  = signalEnvCall()

-----------------------------------
-- EBREAK
-----------------------------------

define System > EBREAK =
    signalException(E_Breakpoint)

-----------------------------------
-- URET
-----------------------------------
define System > URET   =
    NextFetch <- Some(Uret)

-----------------------------------
-- SRET
-----------------------------------
define System > SRET   =
    NextFetch <- Some(Sret)

-----------------------------------
-- HRET
-----------------------------------
define System > HRET   =
    NextFetch <- Some(Hret)

-----------------------------------
-- MRET
-----------------------------------
define System > MRET   =
    NextFetch <- Some(Mret)

-----------------------------------
-- WFI
-----------------------------------
define System > WFI    = nothing

-- Control and Status Registers

bool checkCSROp(csr::imm12, rs1::reg, a::accessType) =
    is_CSR_defined(csr) and check_CSR_access(csrRW(csr), csrPR(csr), curPrivilege, a)

-----------------------------------
-- CSRRW  rd, rs1, imm
-----------------------------------
define System > CSRRW(rd::reg, rs1::reg, csr::imm12) =
    if checkCSROp(csr, rs1, Write)
    then { val = CSR(csr)
         ; writeCSR(csr, GPR(rs1))
         ; writeRD(rd, val)
         }
    else signalException(E_Illegal_Instr)

-----------------------------------
-- CSRRS  rd, rs1, imm
-----------------------------------
define System > CSRRS(rd::reg, rs1::reg, csr::imm12) =
    if checkCSROp(csr, rs1, if rs1 == 0 then Read else Write)
    then { val = CSR(csr)
         ; when rs1 != 0
           do writeCSR(csr, val || GPR(rs1))
         ; writeRD(rd, val)
         }
    else signalException(E_Illegal_Instr)

-----------------------------------
-- CSRRC  rd, rs1, imm
-----------------------------------
define System > CSRRC(rd::reg, rs1::reg, csr::imm12) =
    if checkCSROp(csr, rs1, if rs1 == 0 then Read else Write)
    then { val = CSR(csr)
         ; when rs1 != 0
           do writeCSR(csr, val && ~GPR(rs1))
         ; writeRD(rd, val)
         }
    else signalException(E_Illegal_Instr)

-----------------------------------
-- CSRRWI rd, rs1, imm
-----------------------------------
define System > CSRRWI(rd::reg, zimm::reg, csr::imm12) =
    if checkCSROp(csr, zimm, if zimm == 0 then Read else Write)
    then { val = CSR(csr)
         ; when zimm != 0
           do writeCSR(csr, ZeroExtend(zimm))
         ; writeRD(rd, val)
         }
    else signalException(E_Illegal_Instr)

-----------------------------------
-- CSRRSI rd, rs1, imm
-----------------------------------
define System > CSRRSI(rd::reg, zimm::reg, csr::imm12) =
    if checkCSROp(csr, zimm, if zimm == 0 then Read else Write)
    then { val = CSR(csr)
         ; when zimm != 0
           do writeCSR(csr, val || ZeroExtend(zimm))
         ; writeRD(rd, val)
         }
    else signalException(E_Illegal_Instr)

-----------------------------------
-- CSRRCI rd, rs1, imm
-----------------------------------
define System > CSRRCI(rd::reg, zimm::reg, csr::imm12) =
    if checkCSROp(csr, zimm, if zimm == 0 then Read else Write)
    then { val = CSR(csr)
         ; when zimm != 0
           do writeCSR(csr, val && ~ZeroExtend(zimm))
         ; writeRD(rd, val)
         }
    else signalException(E_Illegal_Instr)

-- Address translation cache flush

-----------------------------------
-- SFENCE.VM
-----------------------------------
define System > SFENCE_VM(rs1::reg) =
{ addr = if rs1 == 0 then None else Some(GPR(rs1))
; match vmType(MCSR.mstatus.M_VM)
  { case Sv32 => { a = if IsSome(addr) then Some(ValOf(addr)<31:0>) else None
                 ; TLB32 <- flushTLB32(curAsid32(), a, TLB32)
                 }
    case Sv39 => { a = if IsSome(addr) then Some(ValOf(addr)<38:0>) else None
                 ; TLB39 <- flushTLB39(curAsid64(), a, TLB39)
                 }
    case _    => #INTERNAL_ERROR("sfence.vm: unimplemented VM model") -- FIXME
  }
}

-----------------------------------
-- Unsupported instructions
-----------------------------------
define UnknownInstruction =
    signalException(E_Illegal_Instr)

-----------------------------------
-- Internal pseudo-instructions
-----------------------------------

-- The argument is the value from the PC.

define Internal > FETCH_MISALIGNED(addr::regType) =
{ signalAddressException(E_Fetch_Misaligned, [addr])
; recordFetchException(addr)
}

define Internal > FETCH_FAULT(addr::regType) =
{ signalAddressException(E_Fetch_Fault, [addr])
; recordFetchException(addr)
}

define Run

--------------------------------------------------
-- Instruction fetch
--------------------------------------------------

construct FetchResult
{ F_Error   :: instruction
, F_Result  :: word
}

FetchResult Fetch() =
{ vPC    = PC
; if vPC<1:0> != 0
  then F_Error(Internal(FETCH_MISALIGNED(vPC)))
  else match translateAddr(vPC, Execute, Instruction)
       { case Some(pPC) => { instw = rawReadInst(pPC)
                           ; setupDelta(vPC, instw)
                           ; F_Result(instw)
                           }
         case None      => F_Error(Internal(FETCH_FAULT(vPC)))
       }
}

---------------------------------------------------------------------------
-- Instruction decoding
---------------------------------------------------------------------------

-- helpers to assemble various immediates from their pieces
imm12 asImm12(imm12::bits(1), imm11::bits(1), immhi::bits(6), immlo::bits(4)) =
    imm12 : imm11 : immhi : immlo

imm20 asImm20(imm20::bits(1), immhi::bits(8), imm11::bits(1), immlo::bits(10)) =
    imm20 : immhi : imm11 : immlo

imm12 asSImm12(immhi::bits(7), immlo::bits(5)) =  immhi : immlo

-- decoders organized by major opcode

instruction decode_LOAD(w::word) =
   match w
   { case 'imm           rs1 000  rd 00000 11' => Load( LB(rd, rs1, imm))
     case 'imm           rs1 001  rd 00000 11' => Load( LH(rd, rs1, imm))
     case 'imm           rs1 010  rd 00000 11' => Load( LW(rd, rs1, imm))
     case 'imm           rs1 011  rd 00000 11' => Load( LD(rd, rs1, imm))
     case 'imm           rs1 100  rd 00000 11' => Load(LBU(rd, rs1, imm))
     case 'imm           rs1 101  rd 00000 11' => Load(LHU(rd, rs1, imm))
     case 'imm           rs1 110  rd 00000 11' => Load(LWU(rd, rs1, imm))
     case _                                    => UnknownInstruction
   }

instruction decode_LOAD_FP(w::word) =
   match w
   { case 'imm           rs1 010  rd 00001 11' => FPLoad(FLW(rd, rs1, imm))
     case 'imm           rs1 011  rd 00001 11' => FPLoad(FLD(rd, rs1, imm))
     case _                                    => UnknownInstruction
   }
instruction decode_MISC_MEM(w::word) =
   match w
   { case '_`4 pred succ rs1 000  rd 00011 11' =>   FENCE(rd, rs1, pred, succ)
     case 'imm           rs1 001  rd 00011 11' => FENCE_I(rd, rs1, imm)
     case _                                    => UnknownInstruction
   }

instruction decode_OP_IMM(w::word) =
   match w
   { case 'imm           rs1 000  rd 00100 11' => ArithI( ADDI(rd, rs1, imm))
     case '000000  shamt rs1 001  rd 00100 11' =>  Shift( SLLI(rd, rs1, shamt))
     case 'imm           rs1 010  rd 00100 11' => ArithI( SLTI(rd, rs1, imm))
     case 'imm           rs1 011  rd 00100 11' => ArithI(SLTIU(rd, rs1, imm))
     case 'imm           rs1 100  rd 00100 11' => ArithI( XORI(rd, rs1, imm))
     case '000000  shamt rs1 101  rd 00100 11' =>  Shift( SRLI(rd, rs1, shamt))
     case '010000  shamt rs1 101  rd 00100 11' =>  Shift( SRAI(rd, rs1, shamt))
     case 'imm           rs1 110  rd 00100 11' => ArithI(  ORI(rd, rs1, imm))
     case 'imm           rs1 111  rd 00100 11' => ArithI( ANDI(rd, rs1, imm))
     case _                                    => UnknownInstruction
   }

instruction decode_OP_IMM_32(w::word) =
   match w
   { case 'imm           rs1 000  rd 00110 11' => ArithI(ADDIW(rd, rs1, imm))
     case '0000000 shamt rs1 001  rd 00110 11' =>  Shift(SLLIW(rd, rs1, shamt))
     case '0000000 shamt rs1 101  rd 00110 11' =>  Shift(SRLIW(rd, rs1, shamt))
     case '0100000 shamt rs1 101  rd 00110 11' =>  Shift(SRAIW(rd, rs1, shamt))
     case _                                    => UnknownInstruction
   }

instruction decode_STORE(w::word) =
   match w
   { case 'ihi       rs2 rs1 000 ilo 01000 11' => Store(SB(rs1, rs2, asSImm12(ihi, ilo)))
     case 'ihi       rs2 rs1 001 ilo 01000 11' => Store(SH(rs1, rs2, asSImm12(ihi, ilo)))
     case 'ihi       rs2 rs1 010 ilo 01000 11' => Store(SW(rs1, rs2, asSImm12(ihi, ilo)))
     case 'ihi       rs2 rs1 011 ilo 01000 11' => Store(SD(rs1, rs2, asSImm12(ihi, ilo)))
     case _                                    => UnknownInstruction
   }

instruction decode_STORE_FP(w::word) =
   match w
   { case 'ihi       rs2 rs1 010 ilo 01001 11' => FPStore(FSW(rs1, rs2, asSImm12(ihi, ilo)))
     case 'ihi       rs2 rs1 011 ilo 01001 11' => FPStore(FSD(rs1, rs2, asSImm12(ihi, ilo)))
     case _                                    => UnknownInstruction
   }

instruction decode_AMO(w::word) =
   match w
   { case '00010 aq rl 00000  rs1 010 rd 01011 11' => AMO(     LR_W(aq, rl, rd, rs1))
     case '00010 aq rl 00000  rs1 011 rd 01011 11' => AMO(     LR_D(aq, rl, rd, rs1))
     case '00011 aq rl rs2    rs1 010 rd 01011 11' => AMO(     SC_W(aq, rl, rd, rs1, rs2))
     case '00011 aq rl rs2    rs1 011 rd 01011 11' => AMO(     SC_D(aq, rl, rd, rs1, rs2))

     case '00001 aq rl rs2    rs1 010 rd 01011 11' => AMO(AMOSWAP_W(aq, rl, rd, rs1, rs2))
     case '00000 aq rl rs2    rs1 010 rd 01011 11' => AMO( AMOADD_W(aq, rl, rd, rs1, rs2))
     case '00100 aq rl rs2    rs1 010 rd 01011 11' => AMO( AMOXOR_W(aq, rl, rd, rs1, rs2))
     case '01100 aq rl rs2    rs1 010 rd 01011 11' => AMO( AMOAND_W(aq, rl, rd, rs1, rs2))
     case '01000 aq rl rs2    rs1 010 rd 01011 11' => AMO(  AMOOR_W(aq, rl, rd, rs1, rs2))
     case '10000 aq rl rs2    rs1 010 rd 01011 11' => AMO( AMOMIN_W(aq, rl, rd, rs1, rs2))
     case '10100 aq rl rs2    rs1 010 rd 01011 11' => AMO( AMOMAX_W(aq, rl, rd, rs1, rs2))
     case '11000 aq rl rs2    rs1 010 rd 01011 11' => AMO(AMOMINU_W(aq, rl, rd, rs1, rs2))
     case '11100 aq rl rs2    rs1 010 rd 01011 11' => AMO(AMOMAXU_W(aq, rl, rd, rs1, rs2))

     case '00001 aq rl rs2    rs1 011 rd 01011 11' => AMO(AMOSWAP_D(aq, rl, rd, rs1, rs2))
     case '00000 aq rl rs2    rs1 011 rd 01011 11' => AMO( AMOADD_D(aq, rl, rd, rs1, rs2))
     case '00100 aq rl rs2    rs1 011 rd 01011 11' => AMO( AMOXOR_D(aq, rl, rd, rs1, rs2))
     case '01100 aq rl rs2    rs1 011 rd 01011 11' => AMO( AMOAND_D(aq, rl, rd, rs1, rs2))
     case '01000 aq rl rs2    rs1 011 rd 01011 11' => AMO(  AMOOR_D(aq, rl, rd, rs1, rs2))
     case '10000 aq rl rs2    rs1 011 rd 01011 11' => AMO( AMOMIN_D(aq, rl, rd, rs1, rs2))
     case '10100 aq rl rs2    rs1 011 rd 01011 11' => AMO( AMOMAX_D(aq, rl, rd, rs1, rs2))
     case '11000 aq rl rs2    rs1 011 rd 01011 11' => AMO(AMOMINU_D(aq, rl, rd, rs1, rs2))
     case '11100 aq rl rs2    rs1 011 rd 01011 11' => AMO(AMOMAXU_D(aq, rl, rd, rs1, rs2))

     case _                                        => UnknownInstruction
   }

instruction decode_OP(w::word) =
   match w
   { case '0000000   rs2 rs1 000  rd 01100 11' => ArithR(  ADD(rd, rs1, rs2))
     case '0100000   rs2 rs1 000  rd 01100 11' => ArithR(  SUB(rd, rs1, rs2))
     case '0000000   rs2 rs1 001  rd 01100 11' =>  Shift(  SLL(rd, rs1, rs2))
     case '0000000   rs2 rs1 010  rd 01100 11' => ArithR(  SLT(rd, rs1, rs2))
     case '0000000   rs2 rs1 011  rd 01100 11' => ArithR( SLTU(rd, rs1, rs2))
     case '0000000   rs2 rs1 100  rd 01100 11' => ArithR(  XOR(rd, rs1, rs2))
     case '0000000   rs2 rs1 101  rd 01100 11' =>  Shift(  SRL(rd, rs1, rs2))
     case '0100000   rs2 rs1 101  rd 01100 11' =>  Shift(  SRA(rd, rs1, rs2))
     case '0000000   rs2 rs1 110  rd 01100 11' => ArithR(   OR(rd, rs1, rs2))
     case '0000000   rs2 rs1 111  rd 01100 11' => ArithR(  AND(rd, rs1, rs2))

     case '0000001   rs2 rs1 000  rd 01100 11' => MulDiv(   MUL(rd, rs1, rs2))
     case '0000001   rs2 rs1 001  rd 01100 11' => MulDiv(  MULH(rd, rs1, rs2))
     case '0000001   rs2 rs1 010  rd 01100 11' => MulDiv(MULHSU(rd, rs1, rs2))
     case '0000001   rs2 rs1 011  rd 01100 11' => MulDiv( MULHU(rd, rs1, rs2))
     case '0000001   rs2 rs1 100  rd 01100 11' => MulDiv(   DIV(rd, rs1, rs2))
     case '0000001   rs2 rs1 101  rd 01100 11' => MulDiv(  DIVU(rd, rs1, rs2))
     case '0000001   rs2 rs1 110  rd 01100 11' => MulDiv(   REM(rd, rs1, rs2))
     case '0000001   rs2 rs1 111  rd 01100 11' => MulDiv(  REMU(rd, rs1, rs2))

     case _                                    => UnknownInstruction
   }

instruction decode_OP_32(w::word) =
   match w
   { case '0000000   rs2 rs1 000  rd 01110 11' => ArithR( ADDW(rd, rs1, rs2))
     case '0100000   rs2 rs1 000  rd 01110 11' => ArithR( SUBW(rd, rs1, rs2))
     case '0000000   rs2 rs1 001  rd 01110 11' =>  Shift( SLLW(rd, rs1, rs2))
     case '0000000   rs2 rs1 101  rd 01110 11' =>  Shift( SRLW(rd, rs1, rs2))
     case '0100000   rs2 rs1 101  rd 01110 11' =>  Shift( SRAW(rd, rs1, rs2))

     case '0000001   rs2 rs1 000  rd 01110 11' => MulDiv(  MULW(rd, rs1, rs2))
     case '0000001   rs2 rs1 100  rd 01110 11' => MulDiv(  DIVW(rd, rs1, rs2))
     case '0000001   rs2 rs1 101  rd 01110 11' => MulDiv( DIVUW(rd, rs1, rs2))
     case '0000001   rs2 rs1 110  rd 01110 11' => MulDiv(  REMW(rd, rs1, rs2))
     case '0000001   rs2 rs1 111  rd 01110 11' => MulDiv( REMUW(rd, rs1, rs2))

     case _                                    => UnknownInstruction
   }

instruction decode_MADD(w::word) =
   match w
   { case 'rs3  00   rs2 rs1 frm  rd 10000 11' => FArith(  FMADD_S(rd, rs1, rs2, rs3, frm))
     case 'rs3  01   rs2 rs1 frm  rd 10000 11' => FArith(  FMADD_D(rd, rs1, rs2, rs3, frm))
     case _                                    => UnknownInstruction
   }

instruction decode_MSUB(w::word) =
   match w
   { case 'rs3  00   rs2 rs1 frm  rd 10001 11' => FArith(  FMSUB_S(rd, rs1, rs2, rs3, frm))
     case 'rs3  01   rs2 rs1 frm  rd 10001 11' => FArith(  FMSUB_D(rd, rs1, rs2, rs3, frm))
     case _                                    => UnknownInstruction
   }

instruction decode_NMSUB(w::word) =
   match w
   { case 'rs3  00   rs2 rs1 frm  rd 10010 11' => FArith( FNMSUB_S(rd, rs1, rs2, rs3, frm))
     case 'rs3  01   rs2 rs1 frm  rd 10010 11' => FArith( FNMSUB_D(rd, rs1, rs2, rs3, frm))
     case _                                    => UnknownInstruction
   }

instruction decode_NMADD(w::word) =
   match w
   { case 'rs3  00   rs2 rs1 frm  rd 10011 11' => FArith( FNMADD_S(rd, rs1, rs2, rs3, frm))
     case 'rs3  01   rs2 rs1 frm  rd 10011 11' => FArith( FNMADD_D(rd, rs1, rs2, rs3, frm))
     case _                                    => UnknownInstruction
   }

instruction decode_OP_FP(w::word) =
   match w
   { case '0000000   rs2 rs1 frm  rd 10100 11' => FArith(   FADD_S(rd, rs1, rs2, frm))
     case '0000100   rs2 rs1 frm  rd 10100 11' => FArith(   FSUB_S(rd, rs1, rs2, frm))
     case '0001000   rs2 rs1 frm  rd 10100 11' => FArith(   FMUL_S(rd, rs1, rs2, frm))
     case '0001100   rs2 rs1 frm  rd 10100 11' => FArith(   FDIV_S(rd, rs1, rs2, frm))
     case '0101100 00000 rs1 frm  rd 10100 11' => FArith(  FSQRT_S(rd, rs1, frm))

     case '0010100   rs2 rs1 000  rd 10100 11' => FArith(  FMIN_S(rd,  rs1, rs2))
     case '0010100   rs2 rs1 001  rd 10100 11' => FArith(  FMAX_S(rd,  rs1, rs2))
     case '1010000   rs2 rs1 010  rd 10100 11' => FArith(   FEQ_S(rd,  rs1, rs2))
     case '1010000   rs2 rs1 001  rd 10100 11' => FArith(   FLT_S(rd,  rs1, rs2))
     case '1010000   rs2 rs1 000  rd 10100 11' => FArith(   FLE_S(rd,  rs1, rs2))

     case '0010000   rs2 rs1 000  rd 10100 11' => FConv (  FSGNJ_S(rd,  rs1, rs2))
     case '0010000   rs2 rs1 001  rd 10100 11' => FConv ( FSGNJN_S(rd,  rs1, rs2))
     case '0010000   rs2 rs1 010  rd 10100 11' => FConv ( FSGNJX_S(rd,  rs1, rs2))

     case '1100000 00000 rs1 frm  rd 10100 11' => FConv(  FCVT_W_S(rd, rs1, frm))
     case '1100000 00001 rs1 frm  rd 10100 11' => FConv( FCVT_WU_S(rd, rs1, frm))
     case '1110000 00000 rs1 000  rd 10100 11' => FConv(   FMV_X_S(rd, rs1))
     case '1110000 00000 rs1 001  rd 10100 11' => FConv(  FCLASS_S(rd, rs1))
     case '1101000 00000 rs1 frm  rd 10100 11' => FConv(  FCVT_S_W(rd, rs1, frm))
     case '1101000 00001 rs1 frm  rd 10100 11' => FConv( FCVT_S_WU(rd, rs1, frm))
     case '1111000 00000 rs1 000  rd 10100 11' => FConv(   FMV_S_X(rd, rs1))

     case '0000001   rs2 rs1 frm  rd 10100 11' => FArith(   FADD_D(rd, rs1, rs2, frm))
     case '0000101   rs2 rs1 frm  rd 10100 11' => FArith(   FSUB_D(rd, rs1, rs2, frm))
     case '0001001   rs2 rs1 frm  rd 10100 11' => FArith(   FMUL_D(rd, rs1, rs2, frm))
     case '0001101   rs2 rs1 frm  rd 10100 11' => FArith(   FDIV_D(rd, rs1, rs2, frm))
     case '0101101 00000 rs1 frm  rd 10100 11' => FArith(  FSQRT_D(rd, rs1, frm))

     case '0010101   rs2 rs1 000  rd 10100 11' => FArith(  FMIN_D(rd,  rs1, rs2))
     case '0010101   rs2 rs1 001  rd 10100 11' => FArith(  FMAX_D(rd,  rs1, rs2))
     case '1010001   rs2 rs1 010  rd 10100 11' => FArith(   FEQ_D(rd,  rs1, rs2))
     case '1010001   rs2 rs1 001  rd 10100 11' => FArith(   FLT_D(rd,  rs1, rs2))
     case '1010001   rs2 rs1 000  rd 10100 11' => FArith(   FLE_D(rd,  rs1, rs2))

     case '0010001   rs2 rs1 000  rd 10100 11' => FConv (  FSGNJ_D(rd,  rs1, rs2))
     case '0010001   rs2 rs1 001  rd 10100 11' => FConv ( FSGNJN_D(rd,  rs1, rs2))
     case '0010001   rs2 rs1 010  rd 10100 11' => FConv ( FSGNJX_D(rd,  rs1, rs2))

     case '1100001 00000 rs1 frm  rd 10100 11' => FConv(  FCVT_W_D(rd, rs1, frm))
     case '1100001 00001 rs1 frm  rd 10100 11' => FConv( FCVT_WU_D(rd, rs1, frm))
     case '1110001 00000 rs1 001  rd 10100 11' => FConv(  FCLASS_D(rd, rs1))
     case '1101001 00000 rs1 frm  rd 10100 11' => FConv(  FCVT_D_W(rd, rs1, frm))
     case '1101001 00001 rs1 frm  rd 10100 11' => FConv( FCVT_D_WU(rd, rs1, frm))

     case '1100000 00010 rs1 frm  rd 10100 11' => FConv(  FCVT_L_S(rd, rs1, frm))
     case '1100000 00011 rs1 frm  rd 10100 11' => FConv( FCVT_LU_S(rd, rs1, frm))
     case '1101000 00010 rs1 frm  rd 10100 11' => FConv(  FCVT_S_L(rd, rs1, frm))
     case '1101000 00011 rs1 frm  rd 10100 11' => FConv( FCVT_S_LU(rd, rs1, frm))

     case '1100001 00010 rs1 frm  rd 10100 11' => FConv(  FCVT_L_D(rd, rs1, frm))
     case '1100001 00011 rs1 frm  rd 10100 11' => FConv( FCVT_LU_D(rd, rs1, frm))
     case '1101001 00010 rs1 frm  rd 10100 11' => FConv(  FCVT_D_L(rd, rs1, frm))
     case '1101001 00011 rs1 frm  rd 10100 11' => FConv( FCVT_D_LU(rd, rs1, frm))
     case '1110001 00000 rs1 000  rd 10100 11' => FConv(   FMV_X_D(rd, rs1))
     case '1111001 00000 rs1 000  rd 10100 11' => FConv(   FMV_D_X(rd, rs1))

     case '0100000 00001 rs1 frm  rd 10100 11' => FConv(  FCVT_S_D(rd, rs1, frm))
     case '0100001 00000 rs1 frm  rd 10100 11' => FConv(  FCVT_D_S(rd, rs1, frm))

     case _                                    => UnknownInstruction
   }

instruction decode_BRANCH(w::word) =
   match w
   { case 'i12 ihi rs2 rs1 000 ilo i11 11000 11' => Branch( BEQ(rs1, rs2, asImm12(i12, i11, ihi, ilo)))
     case 'i12 ihi rs2 rs1 001 ilo i11 11000 11' => Branch( BNE(rs1, rs2, asImm12(i12, i11, ihi, ilo)))
     case 'i12 ihi rs2 rs1 100 ilo i11 11000 11' => Branch( BLT(rs1, rs2, asImm12(i12, i11, ihi, ilo)))
     case 'i12 ihi rs2 rs1 101 ilo i11 11000 11' => Branch( BGE(rs1, rs2, asImm12(i12, i11, ihi, ilo)))
     case 'i12 ihi rs2 rs1 110 ilo i11 11000 11' => Branch(BLTU(rs1, rs2, asImm12(i12, i11, ihi, ilo)))
     case 'i12 ihi rs2 rs1 111 ilo i11 11000 11' => Branch(BGEU(rs1, rs2, asImm12(i12, i11, ihi, ilo)))
     case _                                      => UnknownInstruction
   }

instruction decode_SYSTEM(w::word) =
   match w
   { case 'csr                rs1 001 rd 11100 11' => System( CSRRW(rd, rs1, csr))
     case 'csr                rs1 010 rd 11100 11' => System( CSRRS(rd, rs1, csr))
     case 'csr                rs1 011 rd 11100 11' => System( CSRRC(rd, rs1, csr))
     case 'csr                imm 101 rd 11100 11' => System(CSRRWI(rd, imm, csr))
     case 'csr                imm 110 rd 11100 11' => System(CSRRSI(rd, imm, csr))
     case 'csr                imm 111 rd 11100 11' => System(CSRRCI(rd, imm, csr))

     case '000000000000  00000 000 00000 11100 11' => System( ECALL)
     case '000000000001  00000 000 00000 11100 11' => System(EBREAK)

     case '000000000010  00000 000 00000 11100 11' => System(  URET)
     case '000100000010  00000 000 00000 11100 11' => System(  SRET)
     case '001000000010  00000 000 00000 11100 11' => System(  HRET)
     case '001100000010  00000 000 00000 11100 11' => System(  MRET)

     case '000100000101  00000 000 00000 11100 11' => System(   WFI)

     case '000100000100    rs1 000 00000 11100 11' => System(SFENCE_VM(rs1))

     case _                                        => UnknownInstruction
   }

-- decode by major opcode, except in cases where it has a single instruction
instruction Decode(w::word) =
   match w
   { case 'imm           rs1 000  rd 11001 11' => Branch( JALR(rd, rs1, imm))
     case 'i20 ilo i11 ihi        rd 11011 11' => Branch(  JAL(rd, asImm20(i20, ihi, i11, ilo)))

     case 'imm                    rd 00101 11' => ArithI(AUIPC(rd, imm))
     case 'imm                    rd 01101 11' => ArithI(  LUI(rd, imm))

     case '_`25                      00000 11' => decode_LOAD(w)
     case '_`25                      00001 11' => decode_LOAD_FP(w)
     case '_`25                      00011 11' => decode_MISC_MEM(w)
     case '_`25                      00100 11' => decode_OP_IMM(w)
     case '_`25                      00110 11' => decode_OP_IMM_32(w)

     case '_`25                      01000 11' => decode_STORE(w)
     case '_`25                      01001 11' => decode_STORE_FP(w)
     case '_`25                      01011 11' => decode_AMO(w)
     case '_`25                      01100 11' => decode_OP(w)
     case '_`25                      01110 11' => decode_OP_32(w)

     case '_`25                      10000 11' => decode_MADD(w)
     case '_`25                      10001 11' => decode_MSUB(w)
     case '_`25                      10010 11' => decode_NMSUB(w)
     case '_`25                      10011 11' => decode_NMADD(w)
     case '_`25                      10100 11' => decode_OP_FP(w)

     case '_`25                      11000 11' => decode_BRANCH(w)
     case '_`25                      11100 11' => decode_SYSTEM(w)

     case _                                    => UnknownInstruction
   }

-- instruction printer

string imm(i::bits(N))  = "0x" : [i]
string instr(o::string) = PadRight(#" ", 12, o)

string amotype(aq::amo, rl::amo) =
    match aq, rl
    { case 0, 0 => ""
      case 1, 0 => ".aq"
      case 0, 1 => ".rl"
      case 1, 1 => ".sc"
    }

string pRtype(o::string, rd::reg, rs1::reg, rs2::reg) =
    instr(o) : " " : reg(rd) : ", " : reg(rs1) : ", " : reg(rs2)

string pARtype(o::string, aq::amo, rl::amo, rd::reg, rs1::reg, rs2::reg) =
    pRtype([o : amotype(aq, rl)], rd, rs1, rs2)

string pLRtype(o::string, aq::amo, rl::amo, rd::reg, rs1::reg) =
    instr([o : amotype(aq, rl)]) : " " : reg(rd) : ", " : reg(rs1)

string pItype(o::string, rd::reg, rs1::reg, i::bits(N)) =
    instr(o) : " " : reg(rd) : ", " : reg(rs1) : ", " : imm(i)

string pCSRtype(o::string, rd::reg, rs1::reg, csr::creg) =
    instr(o) : " " : reg(rd) : ", " : reg(rs1) : ", " : csrName(csr)

string pCSRItype(o::string, rd::reg, i::bits(N), csr::creg) =
    instr(o) : " " : reg(rd) : ", " : imm(i) : ", " : csrName(csr)

string pStype(o::string, rs1::reg, rs2::reg, i::bits(N)) =
    instr(o) : " " : reg(rs2) : ", " : reg(rs1) : ", " : imm(i)

string pSBtype(o::string, rs1::reg, rs2::reg, i::bits(N)) =
    instr(o) : " " : reg(rs1) : ", " : reg(rs2) : ", " : imm(i<<1)

string pUtype(o::string, rd::reg, i::bits(N)) =
    instr(o) : " " : reg(rd) : ", " : imm(i)

string pUJtype(o::string, rd::reg, i::bits(N)) =
    instr(o) : " " : reg(rd) : ", " : imm(i<<1)

string pN0type(o::string) =
    instr(o)

string pN1type(o::string, r::reg) =
    instr(o) : " " : reg(r)

string pFRtype(o::string, rd::reg, rs1::reg, rs2::reg) =
    instr(o) : " " : fpreg(rd) : ", " : fpreg(rs1) : ", " : fpreg(rs2)

string pFR1type(o::string, rd::reg, rs::reg) =
    instr(o) : " " : fpreg(rd) : ", " : fpreg(rs)

string pFR3type(o::string, rd::reg, rs1::reg, rs2::reg, rs3::reg) =
    instr(o) : " " : fpreg(rd) : ", " : fpreg(rs1) : ", " : fpreg(rs2) : ", " : fpreg(rs3)

string pFItype(o::string, rd::reg, rs1::reg, i::bits(N)) =
    instr(o) : " " : fpreg(rd) : ", " : reg(rs1) : ", " : imm(i)

string pFStype(o::string, rs1::reg, rs2::reg, i::bits(N)) =
    instr(o) : " " : fpreg(rs2) : ", " : reg(rs1) : ", " : imm(i)

string pCFItype(o::string, rd::reg, rs::reg) =
    instr(o) : " " : fpreg(rd) : ", " : reg(rs)

string pCIFtype(o::string, rd::reg, rs::reg) =
    instr(o) : " " : reg(rd) : ", " : fpreg(rs)

string instructionToString(i::instruction) =
   match i
   { case Branch(  BEQ(rs1, rs2, imm))      => pSBtype("BEQ",  rs1, rs2, imm)
     case Branch(  BNE(rs1, rs2, imm))      => pSBtype("BNE",  rs1, rs2, imm)
     case Branch(  BLT(rs1, rs2, imm))      => pSBtype("BLT",  rs1, rs2, imm)
     case Branch(  BGE(rs1, rs2, imm))      => pSBtype("BGE",  rs1, rs2, imm)
     case Branch( BLTU(rs1, rs2, imm))      => pSBtype("BLTU", rs1, rs2, imm)
     case Branch( BGEU(rs1, rs2, imm))      => pSBtype("BGEU", rs1, rs2, imm)

     case Branch( JALR(rd, rs1, imm))       => pItype("JALR",  rd, rs1, imm)
     case Branch(  JAL(rd, imm))            => pUJtype("JAL",  rd, imm)

     case ArithI(  LUI(rd, imm))            => pUtype("LUI",   rd, imm)
     case ArithI(AUIPC(rd, imm))            => pUtype("AUIPC", rd, imm)

     case ArithI( ADDI(rd, rs1, imm))       => pItype("ADDI",  rd, rs1, imm)
     case  Shift( SLLI(rd, rs1, imm))       => pItype("SLLI",  rd, rs1, imm)
     case ArithI( SLTI(rd, rs1, imm))       => pItype("SLTI",  rd, rs1, imm)
     case ArithI(SLTIU(rd, rs1, imm))       => pItype("SLTIU", rd, rs1, imm)
     case ArithI( XORI(rd, rs1, imm))       => pItype("XORI",  rd, rs1, imm)
     case  Shift( SRLI(rd, rs1, imm))       => pItype("SRLI",  rd, rs1, imm)
     case  Shift( SRAI(rd, rs1, imm))       => pItype("SRAI",  rd, rs1, imm)
     case ArithI(  ORI(rd, rs1, imm))       => pItype("ORI",   rd, rs1, imm)
     case ArithI( ANDI(rd, rs1, imm))       => pItype("ANDI",  rd, rs1, imm)

     case ArithR(  ADD(rd, rs1, rs2))       => pRtype("ADD",   rd, rs1, rs2)
     case ArithR(  SUB(rd, rs1, rs2))       => pRtype("SUB",   rd, rs1, rs2)
     case  Shift(  SLL(rd, rs1, rs2))       => pRtype("SLL",   rd, rs1, rs2)
     case ArithR(  SLT(rd, rs1, rs2))       => pRtype("SLT",   rd, rs1, rs2)
     case ArithR( SLTU(rd, rs1, rs2))       => pRtype("SLTU",  rd, rs1, rs2)
     case ArithR(  XOR(rd, rs1, rs2))       => pRtype("XOR",   rd, rs1, rs2)
     case  Shift(  SRL(rd, rs1, rs2))       => pRtype("SRL",   rd, rs1, rs2)
     case  Shift(  SRA(rd, rs1, rs2))       => pRtype("SRA",   rd, rs1, rs2)
     case ArithR(   OR(rd, rs1, rs2))       => pRtype("OR",    rd, rs1, rs2)
     case ArithR(  AND(rd, rs1, rs2))       => pRtype("AND",   rd, rs1, rs2)

     case ArithI(ADDIW(rd, rs1, imm))       => pItype("ADDIW", rd, rs1, imm)
     case  Shift(SLLIW(rd, rs1, imm))       => pItype("SLLIW", rd, rs1, imm)
     case  Shift(SRLIW(rd, rs1, imm))       => pItype("SRLIW", rd, rs1, imm)
     case  Shift(SRAIW(rd, rs1, imm))       => pItype("SRAIW", rd, rs1, imm)

     case ArithR( ADDW(rd, rs1, rs2))       => pRtype("ADDW",  rd, rs1, rs2)
     case ArithR( SUBW(rd, rs1, rs2))       => pRtype("SUBW",  rd, rs1, rs2)
     case  Shift( SLLW(rd, rs1, rs2))       => pRtype("SLLW",  rd, rs1, rs2)
     case  Shift( SRLW(rd, rs1, rs2))       => pRtype("SRLW",  rd, rs1, rs2)
     case  Shift( SRAW(rd, rs1, rs2))       => pRtype("SRAW",  rd, rs1, rs2)

     case MulDiv(    MUL(rd, rs1, rs2))     => pRtype("MUL",     rd, rs1, rs2)
     case MulDiv(   MULH(rd, rs1, rs2))     => pRtype("MULH",    rd, rs1, rs2)
     case MulDiv( MULHSU(rd, rs1, rs2))     => pRtype("MULHSU",  rd, rs1, rs2)
     case MulDiv(  MULHU(rd, rs1, rs2))     => pRtype("MULHU",   rd, rs1, rs2)
     case MulDiv(    DIV(rd, rs1, rs2))     => pRtype("DIV",     rd, rs1, rs2)
     case MulDiv(   DIVU(rd, rs1, rs2))     => pRtype("DIVU",    rd, rs1, rs2)
     case MulDiv(    REM(rd, rs1, rs2))     => pRtype("REM",     rd, rs1, rs2)
     case MulDiv(   REMU(rd, rs1, rs2))     => pRtype("REMU",    rd, rs1, rs2)

     case MulDiv(   MULW(rd, rs1, rs2))     => pRtype("MULW",    rd, rs1, rs2)
     case MulDiv(   DIVW(rd, rs1, rs2))     => pRtype("DIVW",    rd, rs1, rs2)
     case MulDiv(  DIVUW(rd, rs1, rs2))     => pRtype("DIVUW",   rd, rs1, rs2)
     case MulDiv(   REMW(rd, rs1, rs2))     => pRtype("REMW",    rd, rs1, rs2)
     case MulDiv(  REMUW(rd, rs1, rs2))     => pRtype("REMUW",   rd, rs1, rs2)

     case   Load(   LB(rd, rs1, imm))       => pItype("LB",    rd, rs1, imm)
     case   Load(   LH(rd, rs1, imm))       => pItype("LH",    rd, rs1, imm)
     case   Load(   LW(rd, rs1, imm))       => pItype("LW",    rd, rs1, imm)
     case   Load(   LD(rd, rs1, imm))       => pItype("LD",    rd, rs1, imm)
     case   Load(  LBU(rd, rs1, imm))       => pItype("LBU",   rd, rs1, imm)
     case   Load(  LHU(rd, rs1, imm))       => pItype("LHU",   rd, rs1, imm)
     case   Load(  LWU(rd, rs1, imm))       => pItype("LWU",   rd, rs1, imm)

     case  Store(   SB(rs1, rs2, imm))      => pStype("SB",    rs1, rs2, imm)
     case  Store(   SH(rs1, rs2, imm))      => pStype("SH",    rs1, rs2, imm)
     case  Store(   SW(rs1, rs2, imm))      => pStype("SW",    rs1, rs2, imm)
     case  Store(   SD(rs1, rs2, imm))      => pStype("SD",    rs1, rs2, imm)

     case   FENCE(rd, rs1, pred, succ)      => pN0type("FENCE")
     case FENCE_I(rd, rs1, imm)             => pN0type("FENCE.I")

     case FArith(  FADD_S(rd, rs1, rs2, frm)) => pFRtype("FADD.S", rd, rs1, rs2)
     case FArith(  FSUB_S(rd, rs1, rs2, frm)) => pFRtype("FSUB.S", rd, rs1, rs2)
     case FArith(  FMUL_S(rd, rs1, rs2, frm)) => pFRtype("FMUL.S", rd, rs1, rs2)
     case FArith(  FDIV_S(rd, rs1, rs2, frm)) => pFRtype("FDIV.S", rd, rs1, rs2)

     case FArith( FSQRT_S(rd, rs, frm))       => pFR1type("FSQRT.S", rd, rs)

     case FArith(  FMIN_S(rd, rs1, rs2))      => pFRtype("FMIN.S", rd, rs1, rs2)
     case FArith(  FMAX_S(rd, rs1, rs2))      => pFRtype("FMAX.S", rd, rs1, rs2)
     case FArith(   FEQ_S(rd, rs1, rs2))      => pFRtype("FEQ.S",  rd, rs1, rs2)
     case FArith(   FLT_S(rd, rs1, rs2))      => pFRtype("FLT.S",  rd, rs1, rs2)
     case FArith(   FLE_S(rd, rs1, rs2))      => pFRtype("FLE.S",  rd, rs1, rs2)

     case FArith( FMADD_S(rd, rs1, rs2, rs3, frm)) => pFR3type("FMADD.S",  rd, rs1, rs2, rs3)
     case FArith( FMSUB_S(rd, rs1, rs2, rs3, frm)) => pFR3type("FMSUB.S",  rd, rs1, rs2, rs3)
     case FArith(FNMADD_S(rd, rs1, rs2, rs3, frm)) => pFR3type("FNMADD.S", rd, rs1, rs2, rs3)
     case FArith(FNMSUB_S(rd, rs1, rs2, rs3, frm)) => pFR3type("FNMSUB.S", rd, rs1, rs2, rs3)

     case FArith(  FADD_D(rd, rs1, rs2, frm)) => pFRtype("FADD.D", rd, rs1, rs2)
     case FArith(  FSUB_D(rd, rs1, rs2, frm)) => pFRtype("FSUB.D", rd, rs1, rs2)
     case FArith(  FMUL_D(rd, rs1, rs2, frm)) => pFRtype("FMUL.D", rd, rs1, rs2)
     case FArith(  FDIV_D(rd, rs1, rs2, frm)) => pFRtype("FDIV.D", rd, rs1, rs2)

     case FArith( FSQRT_D(rd, rs, frm))       => pFR1type("FSQRT.D", rd, rs)

     case FArith(  FMIN_D(rd, rs1, rs2))      => pFRtype("FMIN.D", rd, rs1, rs2)
     case FArith(  FMAX_D(rd, rs1, rs2))      => pFRtype("FMAX.D", rd, rs1, rs2)
     case FArith(   FEQ_D(rd, rs1, rs2))      => pFRtype("FEQ.D",  rd, rs1, rs2)
     case FArith(   FLT_D(rd, rs1, rs2))      => pFRtype("FLT.D",  rd, rs1, rs2)
     case FArith(   FLE_D(rd, rs1, rs2))      => pFRtype("FLE.D",  rd, rs1, rs2)

     case FArith( FMADD_D(rd, rs1, rs2, rs3, frm)) => pFR3type("FMADD.D",  rd, rs1, rs2, rs3)
     case FArith( FMSUB_D(rd, rs1, rs2, rs3, frm)) => pFR3type("FMSUB.D",  rd, rs1, rs2, rs3)
     case FArith(FNMADD_D(rd, rs1, rs2, rs3, frm)) => pFR3type("FNMADD.D", rd, rs1, rs2, rs3)
     case FArith(FNMSUB_D(rd, rs1, rs2, rs3, frm)) => pFR3type("FNMSUB.D", rd, rs1, rs2, rs3)

     case FConv(  FSGNJ_S(rd, rs1, rs2))      => pFRtype("FSGNJ.S",    rd, rs1, rs2)
     case FConv( FSGNJN_S(rd, rs1, rs2))      => pFRtype("FSGNJN.S",   rd, rs1, rs2)
     case FConv( FSGNJX_S(rd, rs1, rs2))      => pFRtype("FSGNJX.S",   rd, rs1, rs2)

     case FConv( FCVT_W_S(rd, rs, frm))       => pCIFtype("FCVT.W.S",  rd, rs)
     case FConv(FCVT_WU_S(rd, rs, frm))       => pCIFtype("FCVT.WU.S", rd, rs)
     case FConv(  FMV_X_S(rd, rs))            => pCIFtype("FMV.X.S",   rd, rs)
     case FConv( FCLASS_S(rd, rs))            => pCIFtype("FCLASS.S",  rd, rs)
     case FConv( FCVT_S_W(rd, rs, frm))       => pCFItype("FCVT.S.W",  rd, rs)
     case FConv(FCVT_S_WU(rd, rs, frm))       => pCFItype("FCVT.S.WU", rd, rs)
     case FConv(  FMV_S_X(rd, rs))            => pCFItype("FMV.S.X",   rd, rs)

     case FConv(  FSGNJ_D(rd, rs1, rs2))      => pFRtype("FSGNJ.D",    rd, rs1, rs2)
     case FConv( FSGNJN_D(rd, rs1, rs2))      => pFRtype("FSGNJN.D",   rd, rs1, rs2)
     case FConv( FSGNJX_D(rd, rs1, rs2))      => pFRtype("FSGNJX.D",   rd, rs1, rs2)

     case FConv( FCVT_W_D(rd, rs, frm))       => pCIFtype("FCVT.W.D",  rd, rs)
     case FConv(FCVT_WU_D(rd, rs, frm))       => pCIFtype("FCVT.WU.D", rd, rs)
     case FConv( FCLASS_D(rd, rs))            => pCIFtype("FCLASS.D",  rd, rs)
     case FConv( FCVT_D_W(rd, rs, frm))       => pCFItype("FCVT.D.W",  rd, rs)
     case FConv(FCVT_D_WU(rd, rs, frm))       => pCFItype("FCVT.D.WU", rd, rs)

     case FConv( FCVT_L_S(rd, rs, frm))       => pCIFtype("FCVT.L.S",  rd, rs)
     case FConv(FCVT_LU_S(rd, rs, frm))       => pCIFtype("FCVT.LU.S", rd, rs)
     case FConv( FCVT_S_L(rd, rs, frm))       => pCFItype("FCVT.S.L",  rd, rs)
     case FConv(FCVT_S_LU(rd, rs, frm))       => pCFItype("FCVT.S.LU", rd, rs)
     case FConv( FCVT_L_D(rd, rs, frm))       => pCIFtype("FCVT.L.D",  rd, rs)
     case FConv(FCVT_LU_D(rd, rs, frm))       => pCIFtype("FCVT.LU.D", rd, rs)
     case FConv(  FMV_X_D(rd, rs))            => pCIFtype("FMV.X.D",   rd, rs)
     case FConv( FCVT_D_L(rd, rs, frm))       => pCFItype("FCVT.D.L",  rd, rs)
     case FConv(FCVT_D_LU(rd, rs, frm))       => pCFItype("FCVT.D.LU", rd, rs)
     case FConv(  FMV_D_X(rd, rs))            => pCFItype("FMV.D.X",   rd, rs)
     case FConv( FCVT_D_S(rd, rs, frm))       => pCFItype("FCVT.D.S",  rd, rs)
     case FConv( FCVT_S_D(rd, rs, frm))       => pCFItype("FCVT.S.D",  rd, rs)

     case FPLoad(  FLW(rd, rs1, imm))         => pFItype("FLW",    rd, rs1, imm)
     case FPLoad(  FLD(rd, rs1, imm))         => pFItype("FLD",    rd, rs1, imm)
     case FPStore( FSW(rs1, rs2, imm))        => pFStype("FSW",   rs1, rs2, imm)
     case FPStore( FSD(rs1, rs2, imm))        => pFStype("FSD",   rs1, rs2, imm)

     case AMO(     LR_W(aq, rl, rd, rs1))       => pLRtype("LR.W",      aq, rl, rd, rs1)
     case AMO(     LR_D(aq, rl, rd, rs1))       => pLRtype("LR.D",      aq, rl, rd, rs1)
     case AMO(     SC_W(aq, rl, rd, rs1, rs2))  => pARtype("SC.W",      aq, rl, rd, rs1, rs2)
     case AMO(     SC_D(aq, rl, rd, rs1, rs2))  => pARtype("SC.D",      aq, rl, rd, rs1, rs2)

     case AMO(AMOSWAP_W(aq, rl, rd, rs1, rs2))  => pARtype("AMOSWAP.W", aq, rl, rd, rs1, rs2)
     case AMO( AMOADD_W(aq, rl, rd, rs1, rs2))  => pARtype("AMOADD.W",  aq, rl, rd, rs1, rs2)
     case AMO( AMOXOR_W(aq, rl, rd, rs1, rs2))  => pARtype("AMOXOR.W",  aq, rl, rd, rs1, rs2)
     case AMO( AMOAND_W(aq, rl, rd, rs1, rs2))  => pARtype("AMOAND.W",  aq, rl, rd, rs1, rs2)
     case AMO(  AMOOR_W(aq, rl, rd, rs1, rs2))  => pARtype("AMOOR.W",   aq, rl, rd, rs1, rs2)
     case AMO( AMOMIN_W(aq, rl, rd, rs1, rs2))  => pARtype("AMOMIN.W",  aq, rl, rd, rs1, rs2)
     case AMO( AMOMAX_W(aq, rl, rd, rs1, rs2))  => pARtype("AMOMAX.W",  aq, rl, rd, rs1, rs2)
     case AMO(AMOMINU_W(aq, rl, rd, rs1, rs2))  => pARtype("AMOMINU.W", aq, rl, rd, rs1, rs2)
     case AMO(AMOMAXU_W(aq, rl, rd, rs1, rs2))  => pARtype("AMOMAXU.W", aq, rl, rd, rs1, rs2)

     case AMO(AMOSWAP_D(aq, rl, rd, rs1, rs2))  => pARtype("AMOSWAP.D", aq, rl, rd, rs1, rs2)
     case AMO( AMOADD_D(aq, rl, rd, rs1, rs2))  => pARtype("AMOADD.D",  aq, rl, rd, rs1, rs2)
     case AMO( AMOXOR_D(aq, rl, rd, rs1, rs2))  => pARtype("AMOXOR.D",  aq, rl, rd, rs1, rs2)
     case AMO( AMOAND_D(aq, rl, rd, rs1, rs2))  => pARtype("AMOAND.D",  aq, rl, rd, rs1, rs2)
     case AMO(  AMOOR_D(aq, rl, rd, rs1, rs2))  => pARtype("AMOOR.D",   aq, rl, rd, rs1, rs2)
     case AMO( AMOMIN_D(aq, rl, rd, rs1, rs2))  => pARtype("AMOMIN.D",  aq, rl, rd, rs1, rs2)
     case AMO( AMOMAX_D(aq, rl, rd, rs1, rs2))  => pARtype("AMOMAX.D",  aq, rl, rd, rs1, rs2)
     case AMO(AMOMINU_D(aq, rl, rd, rs1, rs2))  => pARtype("AMOMINU.D", aq, rl, rd, rs1, rs2)
     case AMO(AMOMAXU_D(aq, rl, rd, rs1, rs2))  => pARtype("AMOMAXU.D", aq, rl, rd, rs1, rs2)

     case System( ECALL)                    => pN0type("ECALL")
     case System(EBREAK)                    => pN0type("EBREAK")
     case System(  URET)                    => pN0type("URET")
     case System(  SRET)                    => pN0type("SRET")
     case System(  HRET)                    => pN0type("HRET")
     case System(  MRET)                    => pN0type("MRET")

     case System(   WFI)                    => pN0type("WFI")

     case System( CSRRW(rd, rs1, csr))      => pCSRtype("CSRRW",  rd, rs1, csr)
     case System( CSRRS(rd, rs1, csr))      => pCSRtype("CSRRS",  rd, rs1, csr)
     case System( CSRRC(rd, rs1, csr))      => pCSRtype("CSRRC",  rd, rs1, csr)
     case System(CSRRWI(rd, imm, csr))      => pCSRItype("CSRRWI", rd, imm, csr)
     case System(CSRRSI(rd, imm, csr))      => pCSRItype("CSRRSI", rd, imm, csr)
     case System(CSRRCI(rd, imm, csr))      => pCSRItype("CSRRCI", rd, imm, csr)

     case System(SFENCE_VM(rs1))            => pN1type("SFENCE.VM", rs1)

     case UnknownInstruction                => pN0type("UNKNOWN")

     case Internal(FETCH_MISALIGNED(_))     => pN0type("FETCH_MISALIGNED")
     case Internal(FETCH_FAULT(_))          => pN0type("FETCH_FAULT")
   }


word Rtype(o::opcode, f3::bits(3), rd::reg, rs1::reg, rs2::reg, f7::bits(7)) =
    f7 : rs2 : rs1 : f3 : rd : o

word R4type(o::opcode, f3::bits(3), rd::reg, rs1::reg, rs2::reg, rs3::reg, f2::bits(2)) =
    rs3 : f2 : rs2 : rs1 : f3 : rd : o

word Itype(o::opcode, f3::bits(3), rd::reg, rs1::reg, imm::imm12) =
    imm : rs1 : f3 : rd : o

word Stype(o::opcode, f3::bits(3), rs1::reg, rs2::reg, imm::imm12) =
    imm<11:5> : rs2 : rs1 : f3 : imm<4:0> : o

word SBtype(o::opcode, f3::bits(3), rs1::reg, rs2::reg, imm::imm12) =
    [imm<11>]::bits(1) : imm<9:4> : rs2 : rs1 : f3 : imm<3:0> : [imm<10>]::bits(1) : o

word Utype(o::opcode, rd::reg, imm::imm20) =
    imm : rd : o

word UJtype(o::opcode, rd::reg, imm::imm20) =
    [imm<19>]::bits(1) : imm<9:0> : [imm<10>]::bits(1) : imm<18:11> : rd : o

opcode opc(code::bits(8)) = code<4:0> : '11'

bits(7) amofunc(code::bits(5), aq::amo, rl::amo) =
    code : aq : rl

word Encode(i::instruction) =
   match i
   { case Branch(  BEQ(rs1, rs2, imm))      => SBtype(opc(0x18), 0, rs1, rs2, imm)
     case Branch(  BNE(rs1, rs2, imm))      => SBtype(opc(0x18), 1, rs1, rs2, imm)
     case Branch(  BLT(rs1, rs2, imm))      => SBtype(opc(0x18), 4, rs1, rs2, imm)
     case Branch(  BGE(rs1, rs2, imm))      => SBtype(opc(0x18), 5, rs1, rs2, imm)
     case Branch( BLTU(rs1, rs2, imm))      => SBtype(opc(0x18), 6, rs1, rs2, imm)
     case Branch( BGEU(rs1, rs2, imm))      => SBtype(opc(0x18), 7, rs1, rs2, imm)

     case Branch( JALR(rd, rs1, imm))       =>  Itype(opc(0x19), 0, rd, rs1, imm)
     case Branch(  JAL(rd, imm))            => UJtype(opc(0x1b), rd, imm)

     case ArithI(  LUI(rd, imm))            =>  Utype(opc(0x0D), rd, imm)
     case ArithI(AUIPC(rd, imm))            =>  Utype(opc(0x05), rd, imm)

     case ArithI( ADDI(rd, rs1, imm))       =>  Itype(opc(0x04), 0, rd, rs1, imm)
     case  Shift( SLLI(rd, rs1, imm))       =>  Itype(opc(0x04), 1, rd, rs1, '000000' : imm)
     case ArithI( SLTI(rd, rs1, imm))       =>  Itype(opc(0x04), 2, rd, rs1, imm)
     case ArithI(SLTIU(rd, rs1, imm))       =>  Itype(opc(0x04), 3, rd, rs1, imm)
     case ArithI( XORI(rd, rs1, imm))       =>  Itype(opc(0x04), 4, rd, rs1, imm)
     case  Shift( SRLI(rd, rs1, imm))       =>  Itype(opc(0x04), 5, rd, rs1, '000000' : imm)
     case  Shift( SRAI(rd, rs1, imm))       =>  Itype(opc(0x04), 5, rd, rs1, '010000' : imm)
     case ArithI(  ORI(rd, rs1, imm))       =>  Itype(opc(0x04), 6, rd, rs1, imm)
     case ArithI( ANDI(rd, rs1, imm))       =>  Itype(opc(0x04), 7, rd, rs1, imm)

     case ArithR(  ADD(rd, rs1, rs2))       =>  Rtype(opc(0x0C), 0, rd, rs1, rs2, 0)
     case ArithR(  SUB(rd, rs1, rs2))       =>  Rtype(opc(0x0C), 0, rd, rs1, rs2, 0x20)
     case  Shift(  SLL(rd, rs1, rs2))       =>  Rtype(opc(0x0C), 1, rd, rs1, rs2, 0)
     case ArithR(  SLT(rd, rs1, rs2))       =>  Rtype(opc(0x0C), 2, rd, rs1, rs2, 0)
     case ArithR( SLTU(rd, rs1, rs2))       =>  Rtype(opc(0x0C), 3, rd, rs1, rs2, 0)
     case ArithR(  XOR(rd, rs1, rs2))       =>  Rtype(opc(0x0C), 4, rd, rs1, rs2, 0)
     case  Shift(  SRL(rd, rs1, rs2))       =>  Rtype(opc(0x0C), 5, rd, rs1, rs2, 0)
     case  Shift(  SRA(rd, rs1, rs2))       =>  Rtype(opc(0x0C), 5, rd, rs1, rs2, 0x20)
     case ArithR(   OR(rd, rs1, rs2))       =>  Rtype(opc(0x0C), 6, rd, rs1, rs2, 0)
     case ArithR(  AND(rd, rs1, rs2))       =>  Rtype(opc(0x0C), 7, rd, rs1, rs2, 0)

     case ArithI(ADDIW(rd, rs1, imm))       =>  Itype(opc(0x06), 0, rd, rs1, imm)
     case  Shift(SLLIW(rd, rs1, imm))       =>  Itype(opc(0x06), 1, rd, rs1, '0000000' : imm)
     case  Shift(SRLIW(rd, rs1, imm))       =>  Itype(opc(0x06), 5, rd, rs1, '0000000' : imm)
     case  Shift(SRAIW(rd, rs1, imm))       =>  Itype(opc(0x06), 5, rd, rs1, '0100000' : imm)

     case ArithR( ADDW(rd, rs1, rs2))       =>  Rtype(opc(0x0E), 0, rd, rs1, rs2, '0000000')
     case ArithR( SUBW(rd, rs1, rs2))       =>  Rtype(opc(0x0E), 0, rd, rs1, rs2, '0100000')
     case  Shift( SLLW(rd, rs1, rs2))       =>  Rtype(opc(0x0E), 1, rd, rs1, rs2, '0000000')
     case  Shift( SRLW(rd, rs1, rs2))       =>  Rtype(opc(0x0E), 5, rd, rs1, rs2, '0000000')
     case  Shift( SRAW(rd, rs1, rs2))       =>  Rtype(opc(0x0E), 5, rd, rs1, rs2, '0100000')

     case MulDiv(    MUL(rd, rs1, rs2))     =>  Rtype(opc(0x0C), 0, rd, rs1, rs2, '0000001')
     case MulDiv(   MULH(rd, rs1, rs2))     =>  Rtype(opc(0x0C), 1, rd, rs1, rs2, '0000001')
     case MulDiv( MULHSU(rd, rs1, rs2))     =>  Rtype(opc(0x0C), 2, rd, rs1, rs2, '0000001')
     case MulDiv(  MULHU(rd, rs1, rs2))     =>  Rtype(opc(0x0C), 3, rd, rs1, rs2, '0000001')
     case MulDiv(    DIV(rd, rs1, rs2))     =>  Rtype(opc(0x0C), 4, rd, rs1, rs2, '0000001')
     case MulDiv(   DIVU(rd, rs1, rs2))     =>  Rtype(opc(0x0C), 5, rd, rs1, rs2, '0000001')
     case MulDiv(    REM(rd, rs1, rs2))     =>  Rtype(opc(0x0C), 6, rd, rs1, rs2, '0000001')
     case MulDiv(   REMU(rd, rs1, rs2))     =>  Rtype(opc(0x0C), 7, rd, rs1, rs2, '0000001')

     case MulDiv(   MULW(rd, rs1, rs2))     =>  Rtype(opc(0x0E), 0, rd, rs1, rs2, '0000001')
     case MulDiv(   DIVW(rd, rs1, rs2))     =>  Rtype(opc(0x0E), 4, rd, rs1, rs2, '0000001')
     case MulDiv(  DIVUW(rd, rs1, rs2))     =>  Rtype(opc(0x0E), 5, rd, rs1, rs2, '0000001')
     case MulDiv(   REMW(rd, rs1, rs2))     =>  Rtype(opc(0x0E), 6, rd, rs1, rs2, '0000001')
     case MulDiv(  REMUW(rd, rs1, rs2))     =>  Rtype(opc(0x0E), 7, rd, rs1, rs2, '0000001')

     case   Load(   LB(rd, rs1, imm))       =>  Itype(opc(0x00), 0, rd, rs1, imm)
     case   Load(   LH(rd, rs1, imm))       =>  Itype(opc(0x00), 1, rd, rs1, imm)
     case   Load(   LW(rd, rs1, imm))       =>  Itype(opc(0x00), 2, rd, rs1, imm)
     case   Load(   LD(rd, rs1, imm))       =>  Itype(opc(0x00), 3, rd, rs1, imm)
     case   Load(  LBU(rd, rs1, imm))       =>  Itype(opc(0x00), 4, rd, rs1, imm)
     case   Load(  LHU(rd, rs1, imm))       =>  Itype(opc(0x00), 5, rd, rs1, imm)
     case   Load(  LWU(rd, rs1, imm))       =>  Itype(opc(0x00), 6, rd, rs1, imm)

     case  Store(   SB(rs1, rs2, imm))      =>  Stype(opc(0x08), 0, rs1, rs2, imm)
     case  Store(   SH(rs1, rs2, imm))      =>  Stype(opc(0x08), 1, rs1, rs2, imm)
     case  Store(   SW(rs1, rs2, imm))      =>  Stype(opc(0x08), 2, rs1, rs2, imm)
     case  Store(   SD(rs1, rs2, imm))      =>  Stype(opc(0x08), 3, rs1, rs2, imm)

     case   FENCE(rd, rs1, pred, succ)      =>  Itype(opc(0x03), 0, rd, rs1, '0000' : pred : succ)
     case FENCE_I(rd, rs1, imm)             =>  Itype(opc(0x03), 1, rd, rs1, imm)

     case FArith(  FADD_S(rd, rs1, rs2, frm)) => Rtype(opc(0x14), frm, rd, rs1, rs2, 0x00)
     case FArith(  FSUB_S(rd, rs1, rs2, frm)) => Rtype(opc(0x14), frm, rd, rs1, rs2, 0x04)
     case FArith(  FMUL_S(rd, rs1, rs2, frm)) => Rtype(opc(0x14), frm, rd, rs1, rs2, 0x08)
     case FArith(  FDIV_S(rd, rs1, rs2, frm)) => Rtype(opc(0x14), frm, rd, rs1, rs2, 0x0c)
     case FArith( FSQRT_S(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs,    0, 0x2c)
     case FArith(  FMIN_S(rd, rs1, rs2))      => Rtype(opc(0x14), 0,   rd, rs1, rs2, 0x14)
     case FArith(  FMAX_S(rd, rs1, rs2))      => Rtype(opc(0x14), 1,   rd, rs1, rs2, 0x14)
     case FArith(   FEQ_S(rd, rs1, rs2))      => Rtype(opc(0x14), 2,   rd, rs1, rs2, 0x50)
     case FArith(   FLT_S(rd, rs1, rs2))      => Rtype(opc(0x14), 1,   rd, rs1, rs2, 0x50)
     case FArith(   FLE_S(rd, rs1, rs2))      => Rtype(opc(0x14), 0,   rd, rs1, rs2, 0x50)

     case FArith(  FADD_D(rd, rs1, rs2, frm)) => Rtype(opc(0x14), frm, rd, rs1, rs2, 0x01)
     case FArith(  FSUB_D(rd, rs1, rs2, frm)) => Rtype(opc(0x14), frm, rd, rs1, rs2, 0x05)
     case FArith(  FMUL_D(rd, rs1, rs2, frm)) => Rtype(opc(0x14), frm, rd, rs1, rs2, 0x09)
     case FArith(  FDIV_D(rd, rs1, rs2, frm)) => Rtype(opc(0x14), frm, rd, rs1, rs2, 0x0d)
     case FArith( FSQRT_D(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs,    0, 0x2d)
     case FArith(  FMIN_D(rd, rs1, rs2))      => Rtype(opc(0x14), 0,   rd, rs1, rs2, 0x15)
     case FArith(  FMAX_D(rd, rs1, rs2))      => Rtype(opc(0x14), 1,   rd, rs1, rs2, 0x15)
     case FArith(   FEQ_D(rd, rs1, rs2))      => Rtype(opc(0x14), 2,   rd, rs1, rs2, 0x51)
     case FArith(   FLT_D(rd, rs1, rs2))      => Rtype(opc(0x14), 1,   rd, rs1, rs2, 0x51)
     case FArith(   FLE_D(rd, rs1, rs2))      => Rtype(opc(0x14), 0,   rd, rs1, rs2, 0x51)

     case FPLoad(  FLW(rd, rs1, imm))         => Itype(opc(0x01), 2, rd, rs1, imm)
     case FPLoad(  FLD(rd, rs1, imm))         => Itype(opc(0x01), 3, rd, rs1, imm)
     case FPStore( FSW(rs1, rs2, imm))        => Stype(opc(0x09), 2, rs1, rs2, imm)
     case FPStore( FSD(rs1, rs2, imm))        => Stype(opc(0x09), 3, rs1, rs2, imm)

     case FArith( FMADD_S(rd, rs1, rs2, rs3, frm)) => R4type(opc(0x10), frm, rd, rs1, rs2, rs3, 0)
     case FArith( FMSUB_S(rd, rs1, rs2, rs3, frm)) => R4type(opc(0x11), frm, rd, rs1, rs2, rs3, 0)
     case FArith(FNMSUB_S(rd, rs1, rs2, rs3, frm)) => R4type(opc(0x12), frm, rd, rs1, rs2, rs3, 0)
     case FArith(FNMADD_S(rd, rs1, rs2, rs3, frm)) => R4type(opc(0x13), frm, rd, rs1, rs2, rs3, 0)

     case FArith( FMADD_D(rd, rs1, rs2, rs3, frm)) => R4type(opc(0x10), frm, rd, rs1, rs2, rs3, 1)
     case FArith( FMSUB_D(rd, rs1, rs2, rs3, frm)) => R4type(opc(0x11), frm, rd, rs1, rs2, rs3, 1)
     case FArith(FNMSUB_D(rd, rs1, rs2, rs3, frm)) => R4type(opc(0x12), frm, rd, rs1, rs2, rs3, 1)
     case FArith(FNMADD_D(rd, rs1, rs2, rs3, frm)) => R4type(opc(0x13), frm, rd, rs1, rs2, rs3, 1)

     case FConv(  FSGNJ_S(rd, rs1, rs2))      => Rtype(opc(0x14), 0, rd, rs1, rs2, 0x10)
     case FConv( FSGNJN_S(rd, rs1, rs2))      => Rtype(opc(0x14), 1, rd, rs1, rs2, 0x10)
     case FConv( FSGNJX_S(rd, rs1, rs2))      => Rtype(opc(0x14), 2, rd, rs1, rs2, 0x10)

     case FConv( FCVT_W_S(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 0, 0x60)
     case FConv(FCVT_WU_S(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 1, 0x60)
     case FConv(  FMV_X_S(rd, rs))            => Rtype(opc(0x14), 0,   rd, rs, 0, 0x70)
     case FConv( FCLASS_S(rd, rs))            => Rtype(opc(0x14), 1,   rd, rs, 0, 0x70)
     case FConv( FCVT_S_W(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 0, 0x68)
     case FConv(FCVT_S_WU(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 1, 0x68)
     case FConv(  FMV_S_X(rd, rs))            => Rtype(opc(0x14), 0,   rd, rs, 0, 0x78)

     case FConv(  FSGNJ_D(rd, rs1, rs2))      => Rtype(opc(0x14), 0, rd, rs1, rs2, 0x11)
     case FConv( FSGNJN_D(rd, rs1, rs2))      => Rtype(opc(0x14), 1, rd, rs1, rs2, 0x11)
     case FConv( FSGNJX_D(rd, rs1, rs2))      => Rtype(opc(0x14), 2, rd, rs1, rs2, 0x11)

     case FConv( FCVT_W_D(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 0, 0x61)
     case FConv(FCVT_WU_D(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 1, 0x61)
     case FConv( FCLASS_D(rd, rs))            => Rtype(opc(0x14), 1,   rd, rs, 0, 0x71)
     case FConv( FCVT_D_W(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 0, 0x69)
     case FConv(FCVT_D_WU(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 1, 0x69)
     case FConv( FCVT_S_D(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 1, 0x20)
     case FConv( FCVT_D_S(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 0, 0x21)

     case FConv( FCVT_L_S(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 2, 0x60)
     case FConv(FCVT_LU_S(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 3, 0x60)
     case FConv( FCVT_S_L(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 2, 0x68)
     case FConv(FCVT_S_LU(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 3, 0x68)
     case FConv( FCVT_L_D(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 2, 0x61)
     case FConv(FCVT_LU_D(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 3, 0x61)
     case FConv(  FMV_X_D(rd, rs))            => Rtype(opc(0x14), 0,   rd, rs, 0, 0x71)
     case FConv( FCVT_D_L(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 2, 0x69)
     case FConv(FCVT_D_LU(rd, rs, frm))       => Rtype(opc(0x14), frm, rd, rs, 3, 0x69)
     case FConv(  FMV_D_X(rd, rs))            => Rtype(opc(0x14), 0,   rd, rs, 0, 0x79)

     case AMO(     LR_W(aq, rl, rd, rs1))       => Rtype(opc(0x0B), 2, rd, rs1, 0,   amofunc('00010', aq, rl))
     case AMO(     LR_D(aq, rl, rd, rs1))       => Rtype(opc(0x0B), 3, rd, rs1, 0,   amofunc('00010', aq, rl))
     case AMO(     SC_W(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 2, rd, rs1, rs2, amofunc('00011', aq, rl))
     case AMO(     SC_D(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 3, rd, rs1, rs2, amofunc('00010', aq, rl))

     case AMO(AMOSWAP_W(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 2, rd, rs1, rs2, amofunc('00001', aq, rl))
     case AMO( AMOADD_W(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 2, rd, rs1, rs2, amofunc('00000', aq, rl))
     case AMO( AMOXOR_W(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 2, rd, rs1, rs2, amofunc('00100', aq, rl))
     case AMO( AMOAND_W(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 2, rd, rs1, rs2, amofunc('01100', aq, rl))
     case AMO(  AMOOR_W(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 2, rd, rs1, rs2, amofunc('01000', aq, rl))
     case AMO( AMOMIN_W(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 2, rd, rs1, rs2, amofunc('10000', aq, rl))
     case AMO( AMOMAX_W(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 2, rd, rs1, rs2, amofunc('10100', aq, rl))
     case AMO(AMOMINU_W(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 2, rd, rs1, rs2, amofunc('11000', aq, rl))
     case AMO(AMOMAXU_W(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 2, rd, rs1, rs2, amofunc('11100', aq, rl))

     case AMO(AMOSWAP_D(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 3, rd, rs1, rs2, amofunc('00001', aq, rl))
     case AMO( AMOADD_D(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 3, rd, rs1, rs2, amofunc('00000', aq, rl))
     case AMO( AMOXOR_D(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 3, rd, rs1, rs2, amofunc('00100', aq, rl))
     case AMO( AMOAND_D(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 3, rd, rs1, rs2, amofunc('01100', aq, rl))
     case AMO(  AMOOR_D(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 3, rd, rs1, rs2, amofunc('01000', aq, rl))
     case AMO( AMOMIN_D(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 3, rd, rs1, rs2, amofunc('10000', aq, rl))
     case AMO( AMOMAX_D(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 3, rd, rs1, rs2, amofunc('10100', aq, rl))
     case AMO(AMOMINU_D(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 3, rd, rs1, rs2, amofunc('11000', aq, rl))
     case AMO(AMOMAXU_D(aq, rl, rd, rs1, rs2))  => Rtype(opc(0x0B), 3, rd, rs1, rs2, amofunc('11100', aq, rl))

     case System( ECALL)                    =>  Itype(opc(0x1C), 0, 0, 0, 0x000)
     case System(EBREAK)                    =>  Itype(opc(0x1C), 0, 0, 0, 0x001)
     case System(  URET)                    =>  Itype(opc(0x1C), 0, 0, 0, 0x002)
     case System(  SRET)                    =>  Itype(opc(0x1C), 0, 0, 0, 0x102)
     case System(  HRET)                    =>  Itype(opc(0x1C), 0, 0, 0, 0x202)
     case System(  MRET)                    =>  Itype(opc(0x1C), 0, 0, 0, 0x302)

     case System(   WFI)                    =>  Itype(opc(0x1C), 0, 0, 0, 0x105)

     case System(SFENCE_VM(rs1))            =>  Itype(opc(0x1C), 0, 0, rs1, 0x104)

     case System( CSRRW(rd, rs1, csr))      =>  Itype(opc(0x1C), 1, rd, rs1, csr)
     case System( CSRRS(rd, rs1, csr))      =>  Itype(opc(0x1C), 2, rd, rs1, csr)
     case System( CSRRC(rd, rs1, csr))      =>  Itype(opc(0x1C), 3, rd, rs1, csr)
     case System(CSRRWI(rd, imm, csr))      =>  Itype(opc(0x1C), 5, rd, imm, csr)
     case System(CSRRSI(rd, imm, csr))      =>  Itype(opc(0x1C), 6, rd, imm, csr)
     case System(CSRRCI(rd, imm, csr))      =>  Itype(opc(0x1C), 7, rd, imm, csr)

     case UnknownInstruction                => 0

     case Internal(FETCH_MISALIGNED(_))     => 0
     case Internal(FETCH_FAULT(_))          => 0
   }

---------------------------------------------------------------------------
-- The next state function
---------------------------------------------------------------------------

string log_instruction(w::word, inst::instruction) =
    "instr " : [procID] : " " : [[c_instret(procID)]::nat] :
    " 0x" : hex64(PC) : " : " : hex32(w) : "   " : instructionToString(inst)

nat exitCode() =
    [ExitCode >> 1]::nat

-- The clock/timer factor here is arbitrary, except it that if it is
-- >= approx 200, some 32-bit -pt- tests unexpectedly pass.

nat CYCLES_PER_TIMER_TICK = 200

unit tickClock() =
{ cycles             = c_cycles(procID) + 1
; c_cycles(procID)  <- cycles
; clock             <- cycles div [CYCLES_PER_TIMER_TICK]
}

unit incrInstret() =
    c_instret(procID) <- c_instret(procID) + 1

unit checkTimers() =
{ ()
}

unit Next =
{ match Fetch()
  { case F_Result(w) =>
    { inst = Decode(w)
    ; mark_log(LOG_INSN, log_instruction(w, inst))
    ; Run(inst)
    }
    case F_Error(inst) =>
    { mark_log(LOG_INSN, log_instruction([0::word], inst))
    ; Run(inst)
    }
  }

; tickClock()

  -- Interrupts are prioritized above synchronous traps.
; match NextFetch, curInterrupt()
  { case _, Some(i, delegate) =>
               excHandler(true, interruptIndex(i), curPrivilege, delegate, PC, None)
    case Some(Trap(e)), None =>
             { NextFetch <- None
             ; excIdx = match e.trap
                        { case E_Env_Call => -- convert into privilege-appropriate
                                             -- exception bit-index of {m,h,s}-edeleg
                                             match curPrivilege
                                             { case User       =>  8
                                               case Supervisor =>  9
                                               case Hypervisor => 10
                                               case Machine    => 11
                                             }
                          case _          => excCode(e.trap)
                        }
             ; delegate = excHandlerDelegate(Machine, [excIdx]::nat)
             ; excHandler(false, excIdx, curPrivilege, delegate, PC, e.badaddr)
             }
    case Some(Uret), None =>
             { NextFetch    <- None
             ; MCSR.mstatus <- uret(MCSR.mstatus)
             ; curPrivilege <- User
             ; PC           <- UCSR.uepc
             }
    case Some(Sret), None =>
             { NextFetch    <- None
             ; MCSR.mstatus <- sret(MCSR.mstatus)
             ; curPrivilege <- if MCSR.mstatus.M_SPP then Supervisor else User
             ; PC           <- SCSR.sepc
             }
    case Some(Hret), None =>
             { NextFetch    <- None
             ; MCSR.mstatus <- hret(MCSR.mstatus)
             ; curPrivilege <- match privilege(MCSR.mstatus.M_HPP)
                               { case User        => User
                                 case Supervisor  => Supervisor
                                 case Hypervisor  => Hypervisor
                                 case Machine     => #INTERNAL_ERROR("hret to machine mode")
                               }
             ; PC           <- HCSR.hepc
             }
    case Some(Mret), None =>
             { NextFetch    <- None
             ; MCSR.mstatus <- mret(MCSR.mstatus)
             ; curPrivilege <- privilege(MCSR.mstatus.M_MPP)
             ; PC           <- MCSR.mepc
             }
    case Some(BranchTo(pc)), None =>
             { incrInstret()
             ; NextFetch    <- None
             ; PC           <- pc
             }
    case None, None =>
             { incrInstret()
             ; PC           <- PC + 4
             }
  }
}

unit initIdent(arch::Architecture) =
{ MCSR.misa.ArchBase    <- archBase(arch)
; MCSR.misa.U           <- true
; MCSR.misa.S           <- true
; MCSR.misa.M           <- true
; MCSR.misa.I           <- true

; MCSR.mvendorid        <- MVENDORID
; MCSR.marchid          <- MARCHID
; MCSR.mimpid           <- MIMPID
}

unit initMachine(hartid::id) =
{ -- Startup in Mbare machine mode, with interrupts disabled.
  curPrivilege          <- Machine
; MCSR.&mstatus         <- 0
; MCSR.mstatus.M_VM     <- vmMode(Mbare)
  -- initialize extension context state
; MCSR.mstatus.M_FS     <- ext_status(Initial)
; MCSR.mstatus.M_XS     <- ext_status(Off)
; MCSR.mstatus.M_SD     <- false

  -- Setup hartid
; MCSR.mhartid          <- ZeroExtend(hartid)
  -- Initialize mtvec to lower address (other option is 0xF...FFE00)
; MCSR.mtvec            <- ZeroExtend(0x100`16)
}
-- This initializes each core (via setting procID appropriately) on
-- startup before execution begins.
unit initRegs(pc::nat) =
{ -- TODO: Check if the specs specify the initial values of the registers
  -- on startup.  Initializing to an arbitrary value causes issues with
  -- the verifier, which assumes 0-valued initialization.
  for i in 0 .. 31 do
    gpr([i])   <- 0x0
; for i in 0 .. 31 do
    fpr([i])   <- 0x0

; NextFetch <- Some(BranchTo([pc]))
; PC        <- [pc]
; done      <- false
}
