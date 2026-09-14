using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

class Problem {
    public static List<long> F(List<long> base_list, List<long> nums) {
        base_list.AddRange(nums);
        var res = new List<long>(base_list);
        for (int i = 0; i < nums.Count; i++)
        {
            res.Add(res[res.Count - nums.Count + i]);
        }
        return res;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)9L, (long)7L, (long)5L, (long)3L, (long)1L})), (new List<long>(new long[]{(long)2L, (long)4L, (long)6L, (long)8L, (long)0L}))).SequenceEqual((new List<long>(new long[]{(long)9L, (long)7L, (long)5L, (long)3L, (long)1L, (long)2L, (long)4L, (long)6L, (long)8L, (long)0L, (long)2L, (long)6L, (long)0L, (long)6L, (long)6L}))));
    }

}
