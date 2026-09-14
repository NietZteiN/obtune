using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        foreach (char space in text)
        {
            if (space == ' ')
            {
                text = text.TrimStart();
            }
            else
            {
                text = text.Replace("cd", space.ToString());
            }
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("lorem ipsum")).Equals(("lorem ipsum")));
    }

}
