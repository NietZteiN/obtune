using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> array, long target) {
        long count = 0;
        long i = 1;
        for (int j = 1; j < array.Count; j++) {
            if ((array[j] > array[j - 1]) && (array[j] <= target)) {
                count += i;
            }
            else if (array[j] <= array[j - 1]) {
                i = 1;
            }
            else {
                i++;
            }
        }
        return count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)-1L, (long)4L})), (2L)) == (1L));
    }

}
