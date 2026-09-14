using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(Dictionary<long,string> d, List<long> get_ary) {
        var result = new List<string>();
        foreach (var key in get_ary)
        {
            result.Add(d.GetValueOrDefault(key, null));
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<long,string>(){{3L, "swims like a bull"}}), (new List<long>(new long[]{(long)3L, (long)2L, (long)5L}))).SequenceEqual((new List<object>(new object[]{"swims like a bull", null, null}))));
    }

}
