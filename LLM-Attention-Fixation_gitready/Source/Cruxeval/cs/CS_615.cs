using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> in_list, long num) {
        in_list.Add(num);
        return in_list.IndexOf(in_list.Max());
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)-1L, (long)12L, (long)-6L, (long)-2L})), (-1L)) == (1L));
    }

}
