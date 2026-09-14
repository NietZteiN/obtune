using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> nums, long val) {
        List<long> newList = new List<long>();
        nums.ForEach(i => newList.AddRange(Enumerable.Repeat(i, (int)val)));
        return newList.Sum();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)10L, (long)4L})), (3L)) == (42L));
    }

}
