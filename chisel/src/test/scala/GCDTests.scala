import chisel3._
import chiseltest._
import org.scalatest.flatspec.AnyFlatSpec

class GCDTests extends AnyFlatSpec with ChiselScalatestTester {
  def runGCD(dut : GCD, a : UInt, b : UInt, gcd : UInt, nCycles : Int) = {
    dut.io.in.bits.a.poke(a)
    dut.io.in.bits.b.poke(b)
    dut.io.in.valid.poke(true.B)
    for (i <- 1 to nCycles) {
      dut.io.out.valid.expect(false.B)
      dut.clock.step()
    }
    dut.io.out.valid.expect(true.B)
    dut.io.out.bits.expect(gcd)
  }
  "DUT" should "pass" in {
    test(new GCD) { dut =>

      val list = List(
        (48.U, 32.U, 16.U, 6),
        (7.U, 3.U, 1.U, 8),
        (100.U, 10.U, 10.U, 12)
      )
      for ((a, b, gcd, nCycles) <- list) {
        runGCD(dut, a, b, gcd, nCycles)
        dut.clock.step()
      }
    }
  }
}
