using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<Tuple<string, long>> F(Dictionary<string,long> dic) {
        return dic.OrderBy(x => x.Key).Select(x => Tuple.Create(x.Key, x.Value)).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<string,long>(){{"b", 1L}, {"a", 2L}})).SequenceEqual((new List<Tuple<string, long>>(new Tuple<string, long>[]{(Tuple<string, long>)Tuple.Create("a", 2L), (Tuple<string, long>)Tuple.Create("b", 1L)}))));
    }

}
