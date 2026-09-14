using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums) {
        var l = new List<long>();
        foreach(var i in nums)
        {
            if (!l.Contains(i))
            {
                l.Add(i);
            }
        }
        return l;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)3L, (long)1L, (long)9L, (long)0L, (long)2L, (long)0L, (long)8L}))).SequenceEqual((new List<long>(new long[]{(long)3L, (long)1L, (long)9L, (long)0L, (long)2L, (long)8L}))));
    }

}
