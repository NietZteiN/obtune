using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> lst) {
        List<long> newList = new List<long>();
        int i = lst.Count() - 1;
        for (int j = 0; j < lst.Count(); j++)
        {
            if (i % 2 == 0)
            {
                newList.Add(-lst[i]);
            }
            else
            {
                newList.Add(lst[i]);
            }
            i -= 1;
        }
        return newList;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)7L, (long)-1L, (long)-3L}))).SequenceEqual((new List<long>(new long[]{(long)-3L, (long)1L, (long)7L, (long)-1L}))));
    }

}
