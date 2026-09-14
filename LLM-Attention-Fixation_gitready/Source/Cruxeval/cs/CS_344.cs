using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> lst) {
        Action<List<long>> operation = lst => lst.Reverse();
        var new_list = new List<long>(lst);
        new_list.Sort();
        operation(new_list);
        return lst;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)6L, (long)4L, (long)2L, (long)8L, (long)15L}))).SequenceEqual((new List<long>(new long[]{(long)6L, (long)4L, (long)2L, (long)8L, (long)15L}))));
    }

}
