using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static Tuple<Tuple<string, long>, Tuple<string, long>> F(Dictionary<string,long> d) {
        var enumerator = d.GetEnumerator();
        enumerator.MoveNext();
        var firstItem = enumerator.Current;
        enumerator.MoveNext();
        var secondItem = enumerator.Current;
        return Tuple.Create(Tuple.Create(firstItem.Key, firstItem.Value), Tuple.Create(secondItem.Key, secondItem.Value));
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<string,long>(){{"a", 123L}, {"b", 456L}, {"c", 789L}})).Equals((Tuple.Create(Tuple.Create("a", 123L), Tuple.Create("b", 456L)))));
    }

}
