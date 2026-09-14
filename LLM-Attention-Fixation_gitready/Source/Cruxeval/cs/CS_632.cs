using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> lst) {
        for(int i = lst.Count - 1; i > 0; i--)
        {
            for(int j = 0; j < i; j++)
            {
                if (lst[j] > lst[j + 1])
                {
                    long temp = lst[j];
                    lst[j] = lst[j + 1];
                    lst[j + 1] = temp;
                }
            }
        }
        return lst;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)63L, (long)0L, (long)1L, (long)5L, (long)9L, (long)87L, (long)0L, (long)7L, (long)25L, (long)4L}))).SequenceEqual((new List<long>(new long[]{(long)0L, (long)0L, (long)1L, (long)4L, (long)5L, (long)7L, (long)9L, (long)25L, (long)63L, (long)87L}))));
    }

}
