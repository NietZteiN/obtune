using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> a) {
        if (a.Count >= 2 && a[0] > 0 && a[1] > 0)
        {
            a.Reverse();
            return a;
        }
        a.Add(0);
        return a;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>())).SequenceEqual((new List<long>(new long[]{(long)0L}))));
    }

}
