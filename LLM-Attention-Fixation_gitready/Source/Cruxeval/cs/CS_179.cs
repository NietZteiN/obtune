using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums) {
        // Pass in a copy to avoid modifying nums
        var numsCopy = new List<long>(nums);
        var count = numsCopy.Count;
        for (var i = -count + 1; i < 0; i++)
        {
            numsCopy.Insert(0, numsCopy[numsCopy.Count + i]);
        }
        return numsCopy;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)7L, (long)1L, (long)2L, (long)6L, (long)0L, (long)2L}))).SequenceEqual((new List<long>(new long[]{(long)2L, (long)0L, (long)6L, (long)2L, (long)1L, (long)7L, (long)1L, (long)2L, (long)6L, (long)0L, (long)2L}))));
    }

}
