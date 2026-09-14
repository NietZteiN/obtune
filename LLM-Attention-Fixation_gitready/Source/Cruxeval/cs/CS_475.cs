using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> array, long index) {
        if (index < 0)
        {
            index = array.Count + index;
        }
        return array[(int)index];
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L})), (0L)) == (1L));
    }

}
