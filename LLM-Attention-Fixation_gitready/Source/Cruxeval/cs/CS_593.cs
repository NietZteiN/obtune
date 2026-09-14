using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums, long n) {
        var pos = nums.Count - 1;
        for (var i = -nums.Count; i < 0; i++)
        {
            nums.Insert(pos, nums[nums.Count + i]);
        }
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>()), (14L)).SequenceEqual((new List<long>())));
    }

}
