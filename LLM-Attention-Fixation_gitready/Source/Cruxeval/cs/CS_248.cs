using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> a, List<long> b) {
        a.Sort();
        b.Sort();
        b.Reverse();
        return a.Concat(b).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)666L})), (new List<long>())).SequenceEqual((new List<long>(new long[]{(long)666L}))));
    }

}
