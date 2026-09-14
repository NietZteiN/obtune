using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums) {
        var asc = new List<long>(nums);
        asc.Reverse();
        var desc = asc.Take(asc.Count / 2).ToList();
        return desc.Concat(asc).Concat(desc).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>())).SequenceEqual((new List<long>())));
    }

}
