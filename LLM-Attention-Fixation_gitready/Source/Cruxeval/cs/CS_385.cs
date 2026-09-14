using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> lst) {
        int i = 0;
        List<long> new_list = new List<long>();
        while (i < lst.Count)
        {
            if (lst.Skip(i + 1).Contains(lst[i]))
            {
                new_list.Add(lst[i]);
                if (new_list.Count == 3)
                {
                    return new_list;
                }
            }
            i += 1;
        }
        return new_list;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)0L, (long)2L, (long)1L, (long)2L, (long)6L, (long)2L, (long)6L, (long)3L, (long)0L}))).SequenceEqual((new List<long>(new long[]{(long)0L, (long)2L, (long)2L}))));
    }

}
