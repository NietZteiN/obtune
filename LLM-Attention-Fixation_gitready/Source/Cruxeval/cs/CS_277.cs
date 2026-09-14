using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> lst, long mode) {
        List<long> result = new List<long>(lst);
        if (Convert.ToBoolean(mode))
        {
            result.Reverse();
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)3L, (long)4L})), (1L)).SequenceEqual((new List<long>(new long[]{(long)4L, (long)3L, (long)2L, (long)1L}))));
    }

}
