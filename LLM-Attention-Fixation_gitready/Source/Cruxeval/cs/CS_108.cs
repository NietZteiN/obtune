using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(object var) {
        long amount;
        if (var is List<object> list)
        {
            amount = list.Count;
        }
        else if (var is Dictionary<object, object> dict)
        {
            amount = dict.Keys.Count;
        } 
        else 
        {
            amount = 0;
        }
        return amount > 0 ? amount : 0;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((1L)) == (0L));
    }

}
