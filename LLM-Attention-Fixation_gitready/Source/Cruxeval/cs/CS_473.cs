using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string value) {
        List<int> indexes = new List<int>();
        for (int i = 0; i < text.Length; i++)
        {
            if (text[i].ToString() == value)
            {
                indexes.Add(i);
            }
        }
        List<char> new_text = new List<char>(text.ToCharArray());
        foreach (int i in indexes)
        {
            new_text.Remove(value[0]);
        }
        return new string(new_text.ToArray());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("scedvtvotkwqfoqn"), ("o")).Equals(("scedvtvtkwqfqn")));
    }

}
