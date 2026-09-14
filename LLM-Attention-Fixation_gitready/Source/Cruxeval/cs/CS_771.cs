using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> items) {
        List<long> oddPositioned = new List<long>();
        while (items.Count > 0)
        {
            int position = items.IndexOf(items.Min());
            items.RemoveAt(position);
            long item = items[position];
            oddPositioned.Add(item);
            items.RemoveAt(position);
        }
        return oddPositioned;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)3L, (long)4L, (long)5L, (long)6L, (long)7L, (long)8L}))).SequenceEqual((new List<long>(new long[]{(long)2L, (long)4L, (long)6L, (long)8L}))));
    }

}
