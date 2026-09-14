using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(long temp, long timeLimit) {
        long s = timeLimit / temp;
        long e = timeLimit % temp;
        return s > 1 ? $"{s} {e}" : $"{e} oC";
    }
    public static void Main(string[] args) {
    Debug.Assert(F((1L), (1234567890L)).Equals(("1234567890 0")));
    }

}
