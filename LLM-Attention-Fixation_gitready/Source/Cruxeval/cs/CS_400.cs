using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
class Problem {
    public static string F(string multi_string) {
        var cond_string = multi_string.Split().Select(x => Regex.IsMatch(x, @"^[\x00-\x7F]+$"));
        if (cond_string.Contains(true))
        {
            return string.Join(", ", multi_string.Split().Where(x => Regex.IsMatch(x, @"^[\x00-\x7F]+$")));
        }
        return "";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("I am hungry! eat food.")).Equals(("I, am, hungry!, eat, food.")));
    }

}
