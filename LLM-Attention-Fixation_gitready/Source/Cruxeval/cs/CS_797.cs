using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<Tuple<string, long>> F(Dictionary<string,long> dct) {
        List<Tuple<string, long>> lst = new List<Tuple<string, long>>();
        foreach(var key in dct.Keys.OrderBy(k => k)) {
            lst.Add(new Tuple<string, long>(key, dct[key]));
        }
        return lst;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<string,long>(){{"a", 1L}, {"b", 2L}, {"c", 3L}})).SequenceEqual((new List<Tuple<string, long>>(new Tuple<string, long>[]{(Tuple<string, long>)Tuple.Create("a", 1L), (Tuple<string, long>)Tuple.Create("b", 2L), (Tuple<string, long>)Tuple.Create("c", 3L)}))));
    }

}
