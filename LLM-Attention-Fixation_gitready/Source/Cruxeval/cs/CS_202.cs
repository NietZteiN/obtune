using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array, List<long> lst) {
        array.AddRange(lst);
        return array.Where(e => e >= 10).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)2L, (long)15L})), (new List<long>(new long[]{(long)15L, (long)1L}))).SequenceEqual((new List<long>(new long[]{(long)15L, (long)15L}))));
    }

}
