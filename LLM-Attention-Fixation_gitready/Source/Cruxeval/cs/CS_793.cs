using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> lst, long start, long end) {
        long count = 0;
        for (long i = start; i < end; i++)
        {
            for (long j = i; j < end; j++)
            {
                if (lst[(int)i] != lst[(int)j])
                {
                    count++;
                }
            }
        }
        return count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)4L, (long)3L, (long)2L, (long)1L})), (0L), (3L)) == (3L));
    }

}
