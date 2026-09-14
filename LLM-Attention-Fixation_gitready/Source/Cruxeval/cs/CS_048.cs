using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(List<string> names) {
        if (names.Count == 0)
        {
            return "";
        }
        string smallest = names[0];
        foreach (var name in names.GetRange(1, names.Count - 1))
        {
            if (name.CompareTo(smallest) < 0)
            {
                smallest = name;
            }
        }
        names.Remove(smallest);
        return smallest;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>())).Equals(("")));
    }

}
