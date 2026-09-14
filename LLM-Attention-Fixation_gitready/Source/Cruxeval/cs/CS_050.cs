using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<string> lst) {
        lst.Clear();
        lst.AddRange(Enumerable.Repeat("1", lst.Count + 1));
        return lst.Select(_ => 1L).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"a", (string)"c", (string)"v"}))).SequenceEqual((new List<long>(new long[]{(long)1L}))));
    }

}
