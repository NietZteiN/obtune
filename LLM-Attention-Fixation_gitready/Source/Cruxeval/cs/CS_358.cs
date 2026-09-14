using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {

    public static string F(string text, string value) 
    {
        List<int> indexes = new List<int>();
        for (int i = 0; i < text.Length; i++)
        {
            if (text[i].ToString() == value && (i == 0 || text[i-1].ToString() != value))
            {
                indexes.Add(i);
            }
        }
        if (indexes.Count() % 2 == 1)
        {
            return text;
        }
        return text.Substring(indexes[0] + 1, indexes.Last() - indexes[0] - 1);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("btrburger"), ("b")).Equals(("tr")));
    }

}
