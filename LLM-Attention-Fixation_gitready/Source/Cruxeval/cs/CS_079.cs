using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(List<long> arr) {
        arr.Clear();
        arr.Add(1);
        arr.Add(2);
        arr.Add(3);
        arr.Add(4);
        return string.Join(",", arr);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)0L, (long)1L, (long)2L, (long)3L, (long)4L}))).Equals(("1,2,3,4")));
    }

}
