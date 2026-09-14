using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums, long pos) {
        List<long> subList;
        if (pos % 2 == 1)
        {
            subList = nums.GetRange(0, nums.Count - 1);
            subList.Reverse();
            nums.RemoveRange(0, nums.Count - 1);
            nums.InsertRange(0, subList);
        }
        else
        {
            nums.Reverse();
        }
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)6L, (long)1L})), (3L)).SequenceEqual((new List<long>(new long[]{(long)6L, (long)1L}))));
    }

}
