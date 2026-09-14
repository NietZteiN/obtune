using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(long n, long m) {
        List<long> arr = Enumerable.Range(1, (int)n).Select(x => (long)x).ToList();
        for (int i = 0; i < m; i++)
        {
            arr.Clear();
        }
        return arr;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((1L), (3L)).SequenceEqual((new List<long>())));
    }

}
