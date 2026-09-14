using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> lst) {
        List<long> res = new List<long>();
        for (int i = 0; i < lst.Count; i++)
        {
            if (lst[i] % 2 == 0)
            {
                res.Add(lst[i]);
            }
        }
        return lst.ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)3L, (long)4L}))).SequenceEqual((new List<long>(new long[]{(long)1L, (long)2L, (long)3L, (long)4L}))));
    }

}
