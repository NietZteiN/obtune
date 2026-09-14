using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> lst, long i, long n) {
        lst.Insert((int)i, n);
        return lst;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)44L, (long)34L, (long)23L, (long)82L, (long)24L, (long)11L, (long)63L, (long)99L})), (4L), (15L)).SequenceEqual((new List<long>(new long[]{(long)44L, (long)34L, (long)23L, (long)82L, (long)15L, (long)24L, (long)11L, (long)63L, (long)99L}))));
    }

}
