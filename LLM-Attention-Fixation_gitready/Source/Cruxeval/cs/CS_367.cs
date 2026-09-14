using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums, long rmvalue) {
        List<long> res = nums.ToList();
        while (res.Contains(rmvalue))
        {
            long popped = res[res.IndexOf(rmvalue)];
            if (popped != rmvalue)
            {
                res.Add(popped);
            }
            res.Remove(rmvalue);
        }
        return res;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)6L, (long)2L, (long)1L, (long)1L, (long)4L, (long)1L})), (5L)).SequenceEqual((new List<long>(new long[]{(long)6L, (long)2L, (long)1L, (long)1L, (long)4L, (long)1L}))));
    }

}
