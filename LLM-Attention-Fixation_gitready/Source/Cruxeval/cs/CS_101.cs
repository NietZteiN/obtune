using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array, long i_num, long elem) {
        array.Insert((int)i_num, elem);
        return array;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)-4L, (long)1L, (long)0L})), (1L), (4L)).SequenceEqual((new List<long>(new long[]{(long)-4L, (long)4L, (long)1L, (long)0L}))));
    }

}
