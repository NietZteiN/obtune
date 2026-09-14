using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string value) {
        List<char> ls = text.ToList();
        if (ls.Count(x => x.ToString() == value) % 2 == 0)
        {
            while (ls.Contains(value.ToCharArray()[0]))
            {
                ls.Remove(value.ToCharArray()[0]);
            }
        }
        else
        {
            ls.Clear();
        }
        return string.Join("", ls);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("abbkebaniuwurzvr"), ("m")).Equals(("abbkebaniuwurzvr")));
    }

}
