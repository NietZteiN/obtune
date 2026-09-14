using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> list_x) {
        var item_count = list_x.Count;
        var new_list = new List<long>();
        for (var i = 0; i < item_count; i++)
        {
            new_list.Add(list_x[list_x.Count - 1]);
            list_x.RemoveAt(list_x.Count - 1);
        }
        return new_list;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)5L, (long)8L, (long)6L, (long)8L, (long)4L}))).SequenceEqual((new List<long>(new long[]{(long)4L, (long)8L, (long)6L, (long)8L, (long)5L}))));
    }

}
