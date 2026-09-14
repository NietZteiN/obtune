using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static Tuple<bool, bool> F(Dictionary<string,string> d) {
        var r = new Dictionary<string, Dictionary<string, string>> {
            { "c", new Dictionary<string, string>(d) },
            { "d", new Dictionary<string, string>(d) }
        };
        return new Tuple<bool, bool>(r["c"] == r["d"], r["c"].SequenceEqual(r["d"]));
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<string,string>(){{"i", "1"}, {"love", "parakeets"}})).Equals((Tuple.Create(false, true))));
    }

}
