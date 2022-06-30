import chisel3._
import chisel3.util.{Valid, DeqIO}

class GCDInput extends Bundle {
  val a = UInt(16.W)
  val b = UInt(16.W)
}

class GCD extends Module {
  val io  = IO(new Bundle {
    val in  = DeqIO(new GCDInput())
    val out = Output(Valid(UInt(16.W)))
  })

  val x = Reg(UInt())
  val y = Reg(UInt())
  val p = RegInit(false.B)

  io.in.ready := !p

  when (io.in.valid && !p) {
    x := io.in.bits.a
    y := io.in.bits.b
    p := true.B
  }

  when (p) {
    when (x > y)  { x := y; y := x }
    .otherwise    { y := y - x }
  }

  io.out.bits  := x
  io.out.valid := y === 0.U && p
  when (io.out.valid) {
    p := false.B
  }
}
