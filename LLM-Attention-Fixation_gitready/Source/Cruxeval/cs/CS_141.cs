using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<string> li) {
        List<long> result = new List<long>();
        foreach(string i in li)
        {
            result.Add(li.Count(x => x.Equals(i)));
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"k", (string)"x", (string)"c", (string)"x", (string)"x", (string)"b", (string)"l", (string)"f", (string)"r", (string)"n", (string)"g"}))).SequenceEqual((new List<long>(new long[]{(long)1L, (long)3L, (long)1L, (long)3L, (long)3L, (long)1L, (long)1L, (long)1L, (long)1L, (long)1L, (long)1L}))));
    }

}
