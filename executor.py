import abc
import io
import ast
from contextlib import redirect_stdout


class Executor(abc.ABC):
    @abc.abstractmethod
    def execute(self, code: str) -> str:
        pass


class PythonExecutor(Executor):
    locals = {}

    def execute(self, code: str, variables: dict) -> str:
        output = io.StringIO()

        # Parse the code into an AST.
        tree = ast.parse(code, mode="exec")

        try:
            # Redirect standard output to our StringIO instance.
            with redirect_stdout(output):
                for node in tree.body:
                    PythonExecutor.locals.update(variables)

                    # Compile and execute each node.
                    exec(
                        compile(
                            ast.Module(body=[node], type_ignores=[]), "<ast>", "exec"
                        ),
                        None,
                        PythonExecutor.locals,
                    )

        except Exception as e:
            return str(e)
        
        # Retrieve the output and return it.
        return output.getvalue()


# ----------------------------------------------------------------------------------------------------
# import abc  
# import io  
# import ast  
# from contextlib import redirect_stdout  
# import matplotlib.pyplot as plt  
  
  
# class Executor(abc.ABC):  
#     @abc.abstractmethod  
#     def execute(self, code: str) -> str:  
#         pass  
  
  
# class PythonExecutor(Executor):  
#     locals = {}  
  
#     def execute(self, code: str, variables: dict) -> str:  
#         output = io.StringIO()  
  
#         # Parse the code into an AST.  
#         tree = ast.parse(code, mode="exec")  
  
#         #check if there are any visualization-related elements in the code.  
#         # has_visualization = any(isinstance(node, (ast.Call, ast.ImportFrom, ast.Import)) and (getattr(node.func, 'id', None) in ['plot', 'show', 'figure', 'imshow', 'scatter', 'histogram', 'bar', 'pie', 'plot_surface', 'plot_wireframe', 'plot_trisurf', 'contour', 'contourf']) or (isinstance(node, ast.ImportFrom) and node.module == 'matplotlib.pyplot') for node in ast.walk(tree))  
#         has_visualization = any(  
#             isinstance(node, (ast.Call, ast.ImportFrom)) and  
#             (
#                 (isinstance(node, ast.Call) and hasattr(node.func, 'id') and node.func.id in ['plot', 'show', 'figure', 'imshow', 'scatter', 'histogram', 'bar', 'pie', 'plot_surface', 'plot_wireframe', 'plot_trisurf', 'contour', 'contourf']) or  
#                 (isinstance(node, ast.ImportFrom) and node.module == 'matplotlib.pyplot')  
#             )for node in ast.walk(tree))  

#         plot_data_list = []  
#         if has_visualization:    
#             try:    
#                 exec(    
#                     compile(    
#                         ast.Module(body=[ast.parse(code, mode="exec")], type_ignores=[]), "<ast>", "exec"    
#                     ),    
#                     None,    
#                     variables,    
#                 )    
#             except Exception as e:    
#                 return str(e)    
  
#             try:  
#                 figures = plt.get_fignums()  
#                 for fig_num in figures:  
#                     fig = plt.figure(fig_num)  
#                     plot_data_list.append(fig.canvas.buffer_rgba())  
#             except Exception as e:  
#                 print(str(e))  
                  
#         try:  
#             # Redirect standard output to our StringIO instance.  
#             with redirect_stdout(output):  
#                 for node in tree.body:  
#                     PythonExecutor.locals.update(variables)  
  
#                     # Compile and execute each node.  
#                     exec(  
#                         compile(  
#                             ast.Module(body=[node], type_ignores=[]), "<ast>", "exec"  
#                         ),  
#                         None,  
#                         PythonExecutor.locals,  
#                     )  
  
#         except Exception as e:  
#             return str(e)  
          
#         # Retrieve the output and return it.  
#         else:  
#             return output.getvalue(), plot_data_list  