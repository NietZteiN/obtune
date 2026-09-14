using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<List<long>> lists) {
        lists[1].Clear();
        lists[2].AddRange(lists[1]);
        return lists[0];
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<List<long>>(new List<long>[]{(List<long>)new List<long>(new long[]{(long)395L, (long)666L, (long)7L, (long)4L}), (List<long>)new List<long>(), (List<long>)new List<long>(new long[]{(long)4223L, (long)111L})}))).SequenceEqual((new List<long>(new long[]{(long)395L, (long)666L, (long)7L, (long)4L}))));
    }

}
