using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static Tuple<string, string> F(string key, string value) {
        var dict = new Dictionary<string, string> { { key, value } };
        var item = dict.First();
        dict.Remove(key);
        return Tuple.Create(item.Key, item.Value);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("read"), ("Is")).Equals((Tuple.Create("read", "Is"))));
    }

}
