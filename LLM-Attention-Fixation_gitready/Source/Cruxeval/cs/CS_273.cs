using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string name) {
        string new_name = "";
        name = new string(name.Reverse().ToArray());
        
        foreach (char n in name)
        {
            if (n != '.' && new_name.Count(c => c == '.') < 2)
            {
                new_name = n + new_name;
            }
            else
            {
                break;
            }
        }
        
        return new_name;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((".NET")).Equals(("NET")));
    }

}
